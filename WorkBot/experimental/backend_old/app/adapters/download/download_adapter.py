from backend.app.ports import DownloadPort, DownloadCallback
from backend.storage.file.download_handler import DownloadHandler
from typing import Callable
from pathlib import Path

class DownloadAdapter(DownloadPort):

    def __init__(self, impl: DownloadHandler | None=None) -> None:
        self.impl = impl or DownloadHandler()
        
    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: DownloadCallback,
        timeout: int=10
    ) -> None:
        self.impl.on_download_once(match_fn=match_fn, callback=callback, timeout=timeout)
