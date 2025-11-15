# backend/adapters/downloads/local_download_manager.py
from pathlib import Path
import uuid, shutil, time
from backend.infra.logger import Logger
from dataclasses import dataclass

@dataclass(frozen=True)
class DownloadToken:
    id: str


@Logger.attach_logger
class LocalDownloadManager:
    """
    Full token-based file download manager.
    Bots get opaque tokens, not filesystem paths.
    Managers map tokens -> folders privately.
    """

    def __init__(self, base_downloads_path: Path):
        self.base = base_downloads_path
        self.sessions: dict[str, Path] = {}

    # -------------------------------------------------------------
    # Session creation
    # -------------------------------------------------------------
    def start_session(self) -> DownloadToken:
        token = DownloadToken(id=str(uuid.uuid4()))
        session_dir = (self.base / "sessions" / token.id).resolve()
        session_dir.mkdir(parents=True, exist_ok=True)

        self.sessions[token.id] = session_dir
        self.logger.info(f"[DownloadManager] Session {token.id} -> {session_dir}")

        return token

    # -------------------------------------------------------------
    # Attach Chrome/WebDriver to this session
    # -------------------------------------------------------------
    def attach_to_browser(self, token: DownloadToken, driver) -> None:
        """Configure Chrome to download into the session directory."""
        folder = self.sessions[token.id]

        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": str(folder)
            }
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