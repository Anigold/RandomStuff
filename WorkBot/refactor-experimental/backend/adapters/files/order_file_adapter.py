from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from backend.domain.models.order import Order
from backend.app.ports import OrderFilePort
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore
from backend.domain.serializer.serializers.order import OrderSerializer
from backend.domain.serializer.filename_strategies.order_filename_strategy import OrderFilenameStrategy

class OrderFileAdapter(OrderFilePort):
    """Implements OrderFilePort via the generic file engine."""
    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Order](
            store=LocalBlobStore(),
            serializer=OrderSerializer(),
            namer=OrderFilenameStrategy(),
        )

    # FilePort
    def get_directory(self) -> Path:
        return self._engine.directory()

    def get_file_path(self, obj: Order, format: str = "excel") -> Path:
        fmt = "xlsx" if format in ("excel", "xlsx") else format
        return self._engine.path_for(obj, format=fmt)

    def parse_metadata(self, filename: str) -> dict:
        return self._engine.parse_filename(filename)

    def list_files(self, pattern: str = "*") -> list[Path]:
        return self._engine.list_paths(pattern)

    def read_from_path(self, path: Path) -> Order:
        return self._engine.read(path)

    def save(self, obj: Order, format: str = "excel") -> Path:
        fmt = "xlsx" if format in ("excel", "xlsx") else format
        return self._engine.save(obj, format=fmt, overwrite=True)

    def remove(self, path: Path) -> None:
        self._engine.remove(path)

    def move(self, src: Path, dest: Path, overwrite: bool = False) -> None:
        self._engine.move(src, dest, overwrite=overwrite)

    # Order-specific discovery
    def get_order_files(
        self,
        stores: List[str],
        vendors: List[str],
        formats: Optional[List[str]] = None
    ) -> List[Path]:
        fmts = formats or ["xlsx"]
        results: list[Path] = []
        for f in fmts:
            ext = "xlsx" if f in ("excel", "xlsx") else f
            for p in self.list_files(pattern=f"*.{ext}"):
                meta = self.parse_metadata(p.name)
                if (not stores or meta.get("store") in stores) and (not vendors or meta.get("vendor") in vendors):
                    results.append(p)
        return results

    # helper used by ExpectDownloadedPdf use-case if you need it elsewhere
    def target_pdf_path_for(self, order: Order) -> Path:
        return self.get_file_path(order, format="pdf")
