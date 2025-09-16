# backend/app/application/orders.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from backend.app.ports import OrderFilePort, OrderRepository, DownloadPort
from backend.domain.models.order import Order
from backend.infra.logger import Logger

# Queries
@Logger.attach_logger
@dataclass(frozen=True)
class GetOrderFiles:

    files: OrderFilePort

    def __call__(self, stores: list[str], vendors: list[str], formats: list[str] | None=None) -> list[Path]:
        return self.files.get_order_files(stores, vendors, formats)

@Logger.attach_logger
@dataclass(frozen=True)
class ReadOrderFromFile:

    files: OrderFilePort

    def __call__(self, path: Path) -> Order:  # type: ignore[misc]
        self.logger.info(f"Reading order file: {path}")
        return self.files.get_order_from_file(path)

@Logger.attach_logger
@dataclass(frozen=True)
class ReadOrdersFromFile:

    files: OrderFilePort
    read_order: ReadOrderFromFile

    def __call__(self, paths: list[Path]) -> list[Order]:
        return [self.read_order(path) for path in paths]
        
@Logger.attach_logger
@dataclass(frozen=True)
class ParseFilenameForMetadata:

    files: OrderFilePort

    def __call__(self, order_name: str):
        self.files.parse_filename_for_metadata(order_name)

# Commands
@Logger.attach_logger
@dataclass(frozen=True)
class GenerateVendorUploadFile:

    files: OrderFilePort

    def __call__(self, order: Order, context: dict | None=None) -> Path:
        return self.files.generate_vendor_upload_file(order, context=context)
    
@Logger.attach_logger
@dataclass(frozen=True)
class GenerateVendorUploadFiles:

    get_paths:  GetOrderFiles
    read_order: ReadOrderFromFile
    gen_upload: GenerateVendorUploadFile

    def __call__(
        self,
        stores: list[str],
        vendors: list[str],
        start_date: Optional[str]=None,
        end_date: Optional[str]=None,
        context_map: dict[str, dict] | None=None
    ) -> list[Path]:  # type: ignore[misc]
        
        file_paths = self.get_paths(stores=stores, vendors=vendors, formats=["xlsx"])
        self.logger.info(f"[GenerateVendorUploadFiles] Found {len(file_paths)} order files.")
        outs: list[Path] = []
        for fp in file_paths:
            order = self.read_order(fp)
            ctx = context_map.get(str(fp), {}) if context_map else {}
            outs.append(self.gen_upload(order, ctx))
        return outs
    
@Logger.attach_logger
@dataclass(frozen=True)
class SaveOrderToDB:

    repo: OrderRepository

    def __call__(self, order: Order) -> int: return self.repo.save_order(order)

@Logger.attach_logger
@dataclass(frozen=True)
class SaveOrderToFile:
    
    files: OrderFilePort

    def __call__(self, order: Order, *, format='xlsx', context: dict | None = None) -> None:
        self.files.save(order, format)

@Logger.attach_logger
@dataclass(frozen=True)
class ArchiveOrderFile:

    files: OrderFilePort

    def __call__(self, order: Order) -> None:
        self.files.archive_order_file(order)


@Logger.attach_logger
@dataclass(frozen=True)
class CombineOrders:

    files: OrderFilePort

    def __call__(self, vendors: list[str]) -> None:
        self.files.combine_orders(vendors)

@Logger.attach_logger
@dataclass(frozen=True)
class ExpectDownloadedPdf:

    files: OrderFilePort
    downloads: DownloadPort

    def __call__(self, order: Order) -> None:  # type: ignore[misc]
        def handle(file: Path):
            dest = self.files.get_file_path(order, format="pdf")
            self.files.move(file, dest, overwrite=True)
            self.logger.info(f"Moved downloaded PDF to: {dest}")
        self.downloads.on_download_once(match_fn=lambda f: f.name == "Order.pdf", callback=handle, timeout=30)

# Diff / validation
@Logger.attach_logger
@dataclass(frozen=True)
class CheckAndUpdateOrder:

    files: OrderFilePort

    def __call__(self, order: Order) -> bool:  # type: ignore[misc]
        fp = self.files.get_file_path(order)
        if not fp.exists():
            self.logger.info(f"[Order Update] No existing file at {fp}. Proceeding with save.")
            return False
        try:
            existing = self.files.get_order_from_file(fp)
        except Exception as e:
            self.logger.warning(f"[Order Update] Failed to read existing order file: {e}. Proceeding with overwrite.")
            return False
        if _same(existing, order):
            self.logger.info("[Order Update] Order is unchanged. Skipping overwrite.")
            return True
        self.logger.info("[Order Update] Order has changed. Removing old file.")
        self.files.remove_file(fp)
        pdf = fp.with_suffix(".pdf")
        if pdf.exists(): self.files.remove_file(pdf)
        return False
    
def _same(a: Order, b: Order) -> bool:

    if (a.store != b.store) or (a.vendor != b.vendor) or (a.date != b.date): return False

    def t(i): return (i.sku, i.name, float(i.quantity), float(getattr(i, 'cost_per', 0.0)), float(getattr(i, 'total_cost', 0.0)))
    return set(map(t, a.items)) == set(map(t, b.items))

