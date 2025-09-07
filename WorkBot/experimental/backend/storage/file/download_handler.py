from pathlib import Path
from typing import Callable, Set
import threading
import time
from backend.utils.logger import Logger
from config.paths import DOWNLOADS_PATH


@Logger.attach_logger
class DownloadHandler:
    def __init__(self):
        self.download_dir     = DOWNLOADS_PATH
        self._active_watchers = []

    def on_download(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        poll_interval: float = 0.5
    ) -> None:
        '''
        Starts a persistent background watcher. Calls `callback(file_path)` 
        whenever a new matching, stable file appears.
        '''
        def watcher():
            seen: Set[Path] = set(self.download_dir.iterdir())
            while True:
                current = set(self.download_dir.iterdir())
                new_files = current - seen
                seen = current
                for f in new_files:
                    if match_fn(f) and self._is_stable(f):
                        callback(f)
                time.sleep(poll_interval)

        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()
        self._active_watchers.append(thread)

    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> None:
        '''
        One-shot download watcher. Calls `callback(file_path)` once for a match.
        '''
        def single_watch():
            seen: Set[Path] = set(self.download_dir.iterdir())
            start_time = time.time()

            while time.time() - start_time < timeout:
                current = set(self.download_dir.iterdir())
                new_files = current - seen
                seen = current

                for f in new_files:
                    if match_fn(f) and self._is_stable(f):
                        callback(f)
                        return
                time.sleep(poll_interval)

        thread = threading.Thread(target=single_watch, daemon=True)
        thread.start()
        self._active_watchers.append(thread)

    def move_file(self, src: Path, dest: Path, overwrite: bool = False) -> None:
        if not src.exists():
            raise FileNotFoundError(f'Source file does not exist: {src}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not overwrite:
            raise FileExistsError(f'Destination file already exists: {dest}')
        src.rename(dest)

    def _is_stable(self, path: Path, duration: float = 0.5) -> bool:
        try:
            initial = path.stat().st_size
            time.sleep(duration)
            return path.exists() and path.stat().st_size == initial
        except Exception:
            return False
