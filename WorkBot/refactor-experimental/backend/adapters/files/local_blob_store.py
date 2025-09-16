from __future__ import annotations
import os
import tempfile
import shutil
from pathlib import Path
from typing import Iterable

from backend.app.ports import BlobStore

class LocalBlobStore(BlobStore):
    """
    Local filesystem BlobStore with simple atomic-ish writes:
    - write to temp file in the same directory, then replace/move
    - cross-device moves handled via shutil.move
    """

    def write_bytes(self, path: Path, data: bytes, *, overwrite: bool = False) -> None:
        path = path.resolve()
        self.ensure_dir(path.parent)
        if path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite: {path}")

        # Write to temp then move in place to reduce partial writes risk
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())

        try:
            # On POSIX, replace is atomic; on Windows, use replace if exists else move
            if path.exists():
                os.replace(tmp_path, path)
            else:
                shutil.move(str(tmp_path), str(path))
        finally:
            try:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    def read_bytes(self, path: Path) -> bytes:
        return path.read_bytes()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def remove(self, path: Path) -> None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    def move(self, src: Path, dest: Path, *, overwrite: bool = False) -> None:
        src = src.resolve()
        dest = dest.resolve()
        if not src.exists():
            return
        if dest.exists():
            if overwrite:
                # best-effort replace semantics
                try:
                    os.replace(src, dest)
                    return
                except Exception:
                    dest.unlink(missing_ok=True)
            else:
                raise FileExistsError(f"Destination exists: {dest}")
        self.ensure_dir(dest.parent)
        shutil.move(str(src), str(dest))

    def list_paths(self, base: Path, pattern: str = "*") -> list[Path]:
        base = base.resolve()
        if not base.exists():
            return []
        return sorted(base.glob(pattern))

    def ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
