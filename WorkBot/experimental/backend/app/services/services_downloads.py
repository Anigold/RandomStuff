from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from app.ports import DownloadPort

DestResolver = Callable[[Path], Path]  # given the temp downloaded file, compute final dest

@dataclass(frozen=True)
class DownloadServices:
    downloads: DownloadPort

    def expect_download(
        self,
        *,
        match_fn: Callable[[Path], bool],
        dest_resolver: DestResolver,
        on_moved: Optional[Callable[[Path], None]] = None,
        timeout: int = 30,
        move: Callable[[Path, Path, bool], None] | None = None,  # injected mover (e.g., OrderFilePort.move_file)
        overwrite: bool = True,
    ) -> None:
        """
        Domain-agnostic: wait for a matching file, resolve its destination, move it,
        then optionally run a callback.
        """
        def _callback(src: Path):
            dest = dest_resolver(src)
            if move is None:
                # fail fast: we need a mover supplied by the caller (file port)
                raise RuntimeError("No 'move' function supplied to DownloadServices.expect_download")
            move(src, dest, overwrite)
            if on_moved:
                on_moved(dest)
        self.downloads.on_download_once(match_fn=match_fn, callback=_callback, timeout=timeout)
