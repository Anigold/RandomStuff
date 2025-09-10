from __future__ import annotations
from pathlib import Path
from typing import Callable, Set
import threading
import time

from backend.utils.logger import Logger
from backend.app.ports import DownloadPort


@Logger.attach_logger
class ThreadedDownloadAdapter(DownloadPort):
    """
    Threaded, polling-based DownloadPort adapter.

    - Watches a directory for *new* files.
    - Skips temporary/incomplete extensions (.crdownload, .part, .tmp).
    - Waits for a file to be stable (size unchanged for a short window).
    - Calls the provided callback exactly once for on_download_once.
    """

    def __init__(self, watch_dir: Path, poll_interval: float = 0.5, stable_for: float = 0.5):
        self.download_dir = Path(watch_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.poll_interval = poll_interval
        self.stable_for = stable_for
        self._active_watchers: list[threading.Thread] = []

    # -------- DownloadPort required method --------
    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        timeout: int = 30,
    ) -> None:
        """
        One-shot watcher. Spawns a daemon thread and returns immediately.
        Calls `callback(file_path)` on the first matching, stable file, then stops.
        """
        def single_watch():
            try:
                seen: Set[Path] = set(self._safe_listdir())
                start_time = time.time()

                while time.time() - start_time < timeout:
                    current = set(self._safe_listdir())
                    new_files = current - seen
                    seen = current

                    for f in new_files:
                        if self._is_temp(f):
                            continue
                        if match_fn(f) and self._is_stable(f, self.stable_for):
                            self.logger.info(f"[DownloadOnce] Match detected: {f.name}")
                            try:
                                callback(f)
                            finally:
                                return
                    time.sleep(self.poll_interval)

                self.logger.warning("[DownloadOnce] Timed out waiting for download.")
            except Exception as e:
                self.logger.error(f"[DownloadOnce] Watcher failed: {e}", exc_info=True)

        t = threading.Thread(target=single_watch, daemon=True)
        t.start()
        self._active_watchers.append(t)

    # -------- Optional persistent watcher (handy for debugging/tools) --------
    def on_download(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
    ) -> None:
        """
        Persistent watcher. Calls `callback(file_path)` whenever a new matching, stable file appears.
        Runs forever in a daemon thread.
        """
        def watcher():
            try:
                seen: Set[Path] = set(self._safe_listdir())
                while True:
                    current = set(self._safe_listdir())
                    new_files = current - seen
                    seen = current

                    for f in new_files:
                        if self._is_temp(f):
                            continue
                        if match_fn(f) and self._is_stable(f, self.stable_for):
                            self.logger.info(f"[Download] Match detected: {f.name}")
                            callback(f)
                    time.sleep(self.poll_interval)
            except Exception as e:
                self.logger.error(f"[Download] Watcher failed: {e}", exc_info=True)

        t = threading.Thread(target=watcher, daemon=True)
        t.start()
        self._active_watchers.append(t)

    # -------- Helpers --------
    def _safe_listdir(self) -> list[Path]:
        try:
            return [p for p in self.download_dir.iterdir() if p.is_file()]
        except FileNotFoundError:
            return []

    @staticmethod
    def _is_temp(path: Path) -> bool:
        return path.suffix.lower() in {".crdownload", ".part", ".tmp"}

    @staticmethod
    def _is_stable(path: Path, duration: float) -> bool:
        try:
            size1 = path.stat().st_size
            time.sleep(duration)
            size2 = path.stat().st_size
            return path.exists() and size1 == size2
        except Exception:
            return False
