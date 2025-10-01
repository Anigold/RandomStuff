from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar, Optional

from backend.app.ports.files import GenericFilePort
from backend.app.ports.generic import BlobStore, Serializer, Namer
from backend.infra.logger import Logger

T = TypeVar("T")

@Logger.attach_logger
@dataclass
class GenericFileAdapter(GenericFilePort, Generic[T]):
    '''
    Thin engine for saving/reading domain files using a Namer + Serializer + BlobStore.
    '''
    store:      BlobStore
    serializer: Serializer[T]
    namer:      Namer[T]

    def get_directory(self) -> Path:
        base = self.namer.base_dir()
        self.store.ensure_dir(base)
        return base

    def get_file_path(self, obj: T, format) -> Path:
        return self.namer.path_for(obj, format=format)
    
    def parse_filename(self, filename: str) -> dict:
        return self.namer.parse_filename_for_metadata(filename)
    
    def list_files(self, pattern = "*"):
        return self.store.list_paths(self.directory(), pattern)
    
    def read_from_path(self, path):
        # Prefer serializer.load_path if available
        if hasattr(self.serializer, "load_path"):
            return self.serializer.load_path(path)
        data = self.store.read_bytes(path)
        return self.serializer.loads(data)
    
    def save(self, obj: T, format = None, context: dict | None = None, path_override: Path | None = None):
        fmt = format or self.serializer.preferred_format()

        path = path_override or self.get_file_path(obj, format=fmt)
        self.store.ensure_dir(path.parent)

        data = self.serializer.dumps(obj, format=fmt, context=context)

        self.store.write_bytes(path, data, overwrite=True)
        return path
    
    def remove(self, path):
        self.store.remove(path) if self.store.exists(path) else None

    def move(self, src: Path, dest: Path, overwrite: bool = False) -> None:
        self.store.ensure_dir(dest.parent)
        self.store.move(src, dest, overwrite=overwrite)

    def find(self, **criteria) -> list[T]:
        """
        Find domain objects matching metadata criteria.
        Example: find(vendor="Sysco", store="Bakery")
        """
        matches: list[T] = []
        for path in self.list_files():
            meta = self.parse_filename(path.name)
            if all(meta.get(k) == v for k, v in criteria.items()):
                matches.append(self.read_from_path(path))
        return matches
    
    
    # ----- LEGACY ----- #
    # ----- discovery -----
    # def directory(self) -> Path:
    #     base = self.namer.base_dir()
    #     self.store.ensure_dir(base)
    #     return base

    # def path_for(self, obj: T, *, format: str) -> Path:
    #     return self.namer.path_for(obj, format=format)

    # def list_paths(self, pattern: str = "*") -> list[Path]:
    #     return self.store.list_paths(self.directory(), pattern)

    # def parse_filename(self, filename: str) -> dict:
    #     return self.namer.parse_filename_for_metadata(filename)

    # # ----- read/write -----
    # def save(self, obj: T, *, format: str, context: dict | None = None, overwrite: bool = True) -> Path:
 
    #     fmt = format or self.serializer.preferred_format()

    #     path = self.path_for(obj, format=fmt)
    #     self.store.ensure_dir(path.parent)

    #     data = self.serializer.dumps(obj, format=fmt, context=context)

    #     self.store.write_bytes(path, data, overwrite=overwrite)
    #     return path

    # def read(self, path: Path) -> T:
    #     # Prefer serializer.load_path if available
    #     if hasattr(self.serializer, "load_path"):
    #         return self.serializer.load_path(path)
    #     data = self.store.read_bytes(path)
    #     return self.serializer.loads(data)

    # # ----- file ops -----
    # def remove(self, path: Path) -> None:
    #     if self.store.exists(path):
    #         self.store.remove(path)

    # def move(self, src: Path, dest: Path, *, overwrite: bool = False) -> None:
    #     self.store.ensure_dir(dest.parent)
    #     self.store.move(src, dest, overwrite=overwrite)
