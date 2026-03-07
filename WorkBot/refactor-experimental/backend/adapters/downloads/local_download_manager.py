from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import time
import uuid
from typing import Callable, Optional, Any

from backend.errors.boundaries.infra import InfraBoundary
from backend.infra.logger import Logger


# ==========================================================
# Types
# ==========================================================

@dataclass(frozen=True)
class DownloadToken:
    id: str


@dataclass(frozen=True)
class StagedFile:
    path: Path
    kind: str               # "pdf", "xlsx", etc.
    source: str | None = None  # optional: url/page name/etc.


# ==========================================================
# Download Session (context manager)
# ==========================================================

class DownloadSession:
    """
    Unit-of-work wrapper around LocalDownloadManager.

    - Creates an isolated session dir
    - Attaches Chrome/WebDriver downloads to that dir
    - Lets callers wait for new files matching a pattern
    - Always cleans up the session dir on exit
    """

    def __init__(self, mgr: "LocalDownloadManager", driver: Any):
        self._mgr = mgr
        self._driver = driver
        self._token: Optional[DownloadToken] = None

        

    def __enter__(self) -> "DownloadSession":
        self._token = self._mgr.start_session()
        self._mgr.attach_to_browser(self._token, self._driver)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Always cleanup; callers should persist/move any needed artifacts before exit.
        if self._token is not None:
            self._mgr.cleanup(self._token)
            self._token = None

    def persist(self, files: list[Path], dest_dir: Path) -> list[Path]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        out: list[Path] = []
        for p in files:
            target = dest_dir / p.name
            shutil.copy2(p, target)
            out.append(target)
        return out
    
    @property
    def token(self) -> DownloadToken:
        if self._token is None:
            raise RuntimeError("DownloadSession not started. Use within a 'with' block.")
        return self._token

    def collect(self, pattern: str = "*") -> list[Path]:
        return self._mgr.collect(self.token, pattern=pattern)

    def wait_for(
        self,
        pattern: str,
        timeout: int = 30,
        poll: float = 0.25,
        require_stable: bool = True,
        stable_checks: int = 3,
        stable_poll: float = 0.2,
    ) -> list[Path]:
        """
        Wait until at least one *new* file matching pattern appears.

        require_stable:
            If True, additionally waits until file sizes stop changing across a few checks
            (helps avoid catching partially-written downloads).
        """
        start = time.time()
        seen: set[Path] = set()

        while time.time() - start < timeout:
            files = [p for p in self.collect(pattern) if p not in seen]
            if files:
                if require_stable:
                    files = [p for p in files if self._is_stable_file(p, stable_checks, stable_poll)]
                if files:
                    return files
                # Mark as seen so we don't loop forever on unstable file handles.
                seen.update(files)

            time.sleep(poll)

        return []

    def stage_files(
        self,
        pattern: str,
        kind: str,
        source: str | None = None,
        timeout: int = 30,
        poll: float = 0.25,
    ) -> list[StagedFile]:
        files = self.wait_for(pattern=pattern, timeout=timeout, poll=poll)
        if not files:
            return []

        token = self.token
        staged_dir = (self._mgr.staged_base / token.id).resolve()
        staged_dir.mkdir(parents=True, exist_ok=True)



        persisted: list[StagedFile] = []

        for src in files:
            dest = self._unique_dest(staged_dir / src.name)
            shutil.copy2(src, dest)
            persisted.append(StagedFile(path=dest, kind=kind, source=source))

        return persisted

    def trigger_and_stage(
        self,
        trigger: Callable[[], None],
        pattern: str,
        kind: str,
        source: str | None = None,
        timeout: int = 30,
        poll: float = 0.25,
        require_stable: bool = True,
    ) -> list[StagedFile]:
        """
        Convenience: execute a trigger (e.g., click download) then stage files.
        """
        trigger()
        return self.stage_files(
            pattern=pattern,
            kind=kind,
            source=source,
            timeout=timeout,
            poll=poll,
            require_stable=require_stable,
        )

    def _is_stable_file(self, path: Path, checks: int, poll: float) -> bool:
        """
        Heuristic: file is considered stable if its size remains constant for `checks` reads.
        """
        try:
            last = path.stat().st_size
            for _ in range(checks):
                time.sleep(poll)
                cur = path.stat().st_size
                if cur != last:
                    last = cur
                    # reset stability window by continuing checks
                    # (we don't early-fail because downloads can finish quickly after growth)
            # one more short pause + final check
            time.sleep(poll)
            return path.exists() and path.stat().st_size == last
        except FileNotFoundError:
            return False
        except OSError:
            # If Windows or antivirus temporarily locks file, treat as unstable.
            return False

    def _unique_dest(self, dest: Path) -> Path:
        if not dest.exists():
            return dest

        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        i = 1
        while True:
            candidate = parent / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                return candidate
            i += 1
# ==========================================================
# Local Download Manager
# ==========================================================

@Logger.attach_logger
class LocalDownloadManager:
    """
    Full token-based file download manager + session context wrapper.

    - start_session / attach_to_browser / collect / cleanup remain available
      for low-level usage
    - session(driver) provides the preferred unit-of-work API
    """

    def __init__(self, base_downloads_path: Path):
        self.base = base_downloads_path
        self.sessions: dict[str, Path] = {}
        self.staged_base = (self.base / "staged").resolve()
        self.staged_base.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # Preferred API
    # -------------------------------------------------------------
    def session(self, driver: Any) -> DownloadSession:
        """
        Create a context-managed download session.

        Usage:
            with download_manager.session(driver) as dl:
                ... click download ...
                pdfs = dl.stage_files("*.pdf", kind="pdf", timeout=60)
        """
        return DownloadSession(self, driver)


    # -------------------------------------------------------------
    # Session creation
    # -------------------------------------------------------------
    def start_session(self) -> DownloadToken:
        def operation() -> DownloadToken:
            token = DownloadToken(id=str(uuid.uuid4()))
            session_dir = (self.base / "sessions" / token.id).resolve()
            session_dir.mkdir(parents=True, exist_ok=True)

            self.sessions[token.id] = session_dir
            self.logger.info(f"[DownloadManager] Session {token.id} -> {session_dir}")
            return token

        return InfraBoundary.run(operation)

    # -------------------------------------------------------------
    # Attach Chrome/WebDriver to this session
    # -------------------------------------------------------------
    def attach_to_browser(self, token: DownloadToken, driver: Any) -> None:
        """
        Configure Chrome to download into the session directory.
        Requires Chrome DevTools Protocol support.
        """
        folder = self.sessions[token.id]

        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": str(folder),
            },
        )
        self.logger.debug(f"[DownloadManager] Chrome attached to token {token.id}")

    # -------------------------------------------------------------
    # Collecting downloaded files
    # -------------------------------------------------------------
    def collect(self, token: DownloadToken, pattern: str = "*") -> list[Path]:
        """Return list of files produced during this session."""
        folder = self.sessions[token.id]
        return [f for f in folder.glob(pattern) if f.is_file()]

    # -------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------
    def cleanup(self, token: DownloadToken) -> None:
        folder = self.sessions.get(token.id)
        if folder and folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
            self.logger.info(f"[DownloadManager] Cleaned up {folder}")
        self.sessions.pop(token.id, None)