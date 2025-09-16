from __future__ import annotations
from pathlib import Path
from typing import Protocol, Callable

class DownloadPort(Protocol):
    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        timeout: int = 30,
    ) -> None: ...
