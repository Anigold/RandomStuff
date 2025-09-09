# backend/app/adapters/downloads/download_adapter.py
from __future__ import annotations
import time
from pathlib import Path
from typing import Callable, Optional

from backend.app.ports import DownloadPort

class PollingDownloadAdapter(DownloadPort):
    """
    Poll a directory for a single new/changed file that matches `match_fn`,
    then invoke `callback(path)` and stop. Good enough for browser downloads.
    """
    def __init__(self, watch_dir: Path, poll_interval: float = 0.5):
        self.watch_dir = Path(watch_dir)
        self.poll_interval = poll_interval
        self.watch_dir.mkdir(parents=True, exist_ok=True)

    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        timeout: int = 30,
    ) -> None:
        deadline = time.time() + timeout
        seen: set[Path] = set(p.resolve() for p in self.watch_dir.iterdir())

        while time.time() < deadline:
            for p in self.watch_dir.iterdir():
                rp = p.resolve()
                if rp in seen:
                    continue
                # ignore temp/incomplete files (.crdownload/.part, etc.)
                if rp.suffix.lower() in {".crdownload", ".part", ".tmp"}:
                    continue
                if match_fn(rp):
                    try:
                        callback(rp)
                    finally:
                        return
                seen.add(rp)
            time.sleep(self.poll_interval)

        # Optional: raise or log timeout; keeping it silent is OK if caller logs.
        # raise TimeoutError("Download not detected before timeout")
