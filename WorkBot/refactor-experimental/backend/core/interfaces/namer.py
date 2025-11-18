from __future__ import annotations
from typing import Protocol, Generic, TypeVar, Any
from pathlib import Path

T = TypeVar('T')

class Namer(Protocol, Generic[T]):
    '''Decide where & how files are named on disk.'''
    def base_dir(self) -> Path: ...
    def filename(self, obj: T, *, format: str) -> str: ...
    def parse_filename_for_metadata(self, filename: str) -> dict[str, Any]: ...
    def path_for(self, obj: T) -> Path: ...
    def parse_path_metadata(self, path: Path) -> dict[str, Any]:
        return self.parse_filename_for_metadata(path.name)