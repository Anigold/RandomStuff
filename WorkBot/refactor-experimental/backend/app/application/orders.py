from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable

from backend.app.ports import OrderRepository, DownloadPort
from backend.domain.models import Order
from backend.infra.logger import Logger


# ========== QUERIES ==========

@Logger.attach_logger
@dataclass(frozen=True)
class ListOrders:
    repo: OrderRepository
    def __call__(self) -> list[Order]:
        self.logger.info("Listing all orders")
        return self.repo.list_orders()


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrdersByVendor:
    repo: OrderRepository
    def __call__(self, vendor: str) -> list[Order]:
        self.logger.info(f"Listing orders for vendor={vendor}")
        return self.repo.list_by_vendor(vendor)


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrdersByStore:
    repo: OrderRepository
    def __call__(self, store: str) -> list[Order]:
        self.logger.info(f"Listing orders for store={store}")
        return self.repo.list_by_store(store)


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrder:
    repo: OrderRepository
    def __call__(self, vendor: str, store: str, date: Optional[str] = None) -> Order:
        self.logger.info(f"Getting order vendor={vendor}, store={store}, date={date}")
        return self.repo.get_order(vendor, store, date)


# ========== COMMANDS ==========

@Logger.attach_logger
@dataclass(frozen=True)
class SaveOrder:
    repo: OrderRepository
    def __call__(self, order: Order) -> int:
        self.logger.info(f"Saving order {order.vendor} / {order.store} / {order.date}")
        return self.repo.save_order(order)


@Logger.attach_logger
@dataclass(frozen=True)
class RemoveOrder:
    repo: OrderRepository
    def __call__(self, vendor: str, store: str, date: Optional[str] = None) -> None:
        self.logger.info(f"Removing order vendor={vendor}, store={store}, date={date}")
        self.repo.remove_order(vendor, store, date)


@Logger.attach_logger
@dataclass(frozen=True)
class GenerateVendorUploadFile:
    """
    Delegates vendor upload file generation to the repository.
    The repository hides file/format specifics.
    """
    repo: OrderRepository
    def __call__(self, order: Order, context: dict | None = None):
        self.logger.info(f"Generating vendor upload for {order.vendor} / {order.store} / {order.date}")
        return self.repo.generate_vendor_upload_file(order, context)


@Logger.attach_logger
@dataclass(frozen=True)
class GenerateVendorUploadFiles:
    """
    Domain-first batching:
      - Discover orders via repository (no path/format in app layer)
      - Generate each vendor upload through repository
    """
    list_by_vendor: GetOrdersByVendor
    gen_upload: GenerateVendorUploadFile

    def __call__(
        self,
        vendors: list[str],
        start_date: Optional[str] = None,   # reserved for future repo filters
        end_date: Optional[str] = None,     # reserved for future repo filters
        context_map: dict[str, dict] | None = None
    ) -> list:
        outs = []
        for vendor in vendors:
            orders = self.list_by_vendor(vendor)
            self.logger.info(f"[GenerateVendorUploadFiles] vendor={vendor} orders={len(orders)}")
            for order in orders:
                key = f"{order.vendor}|{order.store}|{order.date}"
                ctx = context_map.get(key, {}) if context_map else {}
                outs.append(self.gen_upload(order, ctx))
        return outs


@Logger.attach_logger
@dataclass(frozen=True)
class ExpectDownloadedPdf:
    """
    Watches for one download and delegates ingesting it to the repository.
    App layer doesn't compute paths or change suffixes.
    """
    repo: OrderRepository
    downloads: DownloadPort

    def __call__(self, order: Order, match: Optional[Callable] = None, timeout: int = 30) -> None:
        self.logger.info(f"Expecting downloaded PDF for {order.vendor} / {order.store} / {order.date}")

        # Default match rule if caller doesn't provide one
        matcher = match or (lambda f: f.name.lower().endswith(".pdf"))

        def handle(file_path):
            # Delegate the storage/placement details to the repository.
            self.repo.ingest_downloaded_attachment(order, src_path=file_path, kind="pdf")
            self.logger.info(f"Ingested downloaded PDF: {file_path}")

        self.downloads.on_download_once(match_fn=matcher, callback=handle, timeout=timeout)


# ========== DIFF / VALIDATION ==========

@Logger.attach_logger
@dataclass(frozen=True)
class CheckAndUpdateOrder:
    """
    Returns True if an equivalent order already exists (no update needed).
    Returns False if no existing order or if it differs (caller can proceed to save).
    No direct file IO here; we use repo.get(...) to fetch existing if present.
    """
    repo: OrderRepository

    def __call__(self, order: Order) -> bool:
        try:
            existing = self.repo.get_order(order.vendor, order.store, date=order.date)
        except FileNotFoundError:
            self.logger.info("[Order Update] No existing order found for same vendor/store/date")
            return False
        except Exception as e:
            self.logger.warning(f"[Order Update] Failed to fetch existing order: {e}. Proceeding as changed.")
            return False

        same = _same(existing, order)
        self.logger.info("[Order Update] Unchanged — skip overwrite." if same else "[Order Update] Changed — overwrite needed.")
        return same


# ========== DOMAIN COMPARISON HELPERS ==========

def _same(a: Order, b: Order) -> bool:
    if (a.store != b.store) or (a.vendor != b.vendor) or (a.date != b.date):
        return False

    def normalize(item):
        return (
            item.sku,
            item.name,
            float(item.quantity),
            float(getattr(item, "cost_per", 0.0)),
            float(getattr(item, "total_cost", 0.0)),
        )

    return set(map(normalize, a.items)) == set(map(normalize, b.items))
