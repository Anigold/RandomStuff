from __future__ import annotations
from pathlib import Path
from typing import Protocol, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class DownloadToken:
    id: str


class DownloadPort(Protocol):
    def on_download_once(
        self,
        match_fn: Callable[[Path], bool],
        callback: Callable[[Path], None],
        timeout: int = 30,
    ) -> None: ...


class DownloadManagerPort:

    def start_session(self, name: str) -> Path:
        """Create an isolated folder for a new download session."""
        ...

    def attach_to_browser(self, folder: Path, pattern: str, timeout: int) -> Path:
        """Wait for a file matching pattern to appear."""
        ...

    def collect(self, token: DownloadToken, pattern: str = "*") -> list[Path]:
        """Return all matching files."""
        ...

    def cleanup(self, folder: Path) -> None:
        """Remove a temp folder after ingestion."""
        ...
