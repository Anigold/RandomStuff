from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar, Optional

from backend.app.ports.generic import BlobStore, Serializer, Namer

T = TypeVar("T")

@dataclass
class GenericFileAdapter(Generic[T]):
    '''
    Thin engine for saving/reading domain files using a Namer + Serializer + BlobStore.
    '''
    store:      BlobStore
    serializer: Serializer[T]
    namer:      Namer[T]

    # ----- discovery -----
    def directory(self) -> Path:
        base = self.namer.base_dir()
        self.store.ensure_dir(base)
        return base

    def path_for(self, obj: T, *, format: str) -> Path:
        base = self.directory()
        name = self.namer.filename(obj, format=format)
        return (base / name).resolve()

    def list_paths(self, pattern: str = "*") -> list[Path]:
        return self.store.list_paths(self.directory(), pattern)

    def parse_filename(self, filename: str) -> dict:
        return self.namer.parse_metadata(filename)

    # ----- read/write -----
    def save(self, obj: T, *, format: str, overwrite: bool = True) -> Path:
        path = self.path_for(obj, format=format)
        self.store.ensure_dir(path.parent)
        data = self.serializer.dumps(obj, format=format)
        self.store.write_bytes(path, data, overwrite=overwrite)
        return path

    def read(self, path: Path) -> T:
        # Prefer serializer.load_path if available
        if hasattr(self.serializer, "load_path"):
            return self.serializer.load_path(path)  # type: ignore[attr-defined]
        data = self.store.read_bytes(path)
        return self.serializer.loads(data)

    # ----- file ops -----
    def remove(self, path: Path) -> None:
        if self.store.exists(path):
            self.store.remove(path)

    def move(self, src: Path, dest: Path, *, overwrite: bool = False) -> None:
        self.store.ensure_dir(dest.parent)
        self.store.move(src, dest, overwrite=overwrite)
