from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    OrderRepository, 
    DownloadManagerPort
)


from dataclasses import dataclass
from typing import Optional, Callable, List
from pathlib import Path
from pprint import pprint

from backend.app.ports import OrderRepository, DownloadManagerPort
from backend.domain.models import Order
from backend.infra.logger import Logger


# ========== QUERIES ==========

@Logger.attach_logger
@dataclass(frozen=True)
class ListOrders:
    repo: OrderRepository
    def __call__(self) -> List[Order]:
        self.logger.info("Listing all orders")
        return self.repo.list_all()


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrdersByVendor:
    repo: OrderRepository
    def __call__(self, vendor: str) -> List[Order]:
        self.logger.info(f"Listing orders for vendor={vendor}")
        return self.repo.list_by_vendor(vendor)


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrdersByStore:
    repo: OrderRepository
    def __call__(self, store: str) -> List[Order]:
        self.logger.info(f"Listing orders for store={store}")
        return self.repo.list_by_store(store)


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrder:
    repo: OrderRepository
    def __call__(self, store: str, vendor: str, date: Optional[str] = None) -> Order:
        return self.repo.get(store, vendor, date)


@Logger.attach_logger
@dataclass(frozen=True)
class GetOrders:

    repo:      OrderRepository
    get_order: GetOrder
    
    def __call__(self, stores: str, vendors: str, dates: Optional[List[str]] = None) -> List[Order]:
        self.logger.info(f"Getting orders: vendors={vendors}, stores={stores}, dates={dates}")
        orders = []
        for vendor in vendors:
            for store in stores:
                if not dates:
                    order = self.get_order(store, vendor)
                    if not order: continue
                    orders.append(order)
        self.logger.info(f'Retrieved {len(orders)} orders.')
        return orders

# ========== COMMANDS ==========

@Logger.attach_logger
@dataclass(frozen=True)
class CombineOrders:

    repo : OrderRepository
    list_by_vendor: GetOrdersByVendor

    def __call__(self, vendors: List[str]) -> None:
        self.logger.info(f'Merging all orders for: {vendors}')
        for vendor in vendors:
            orders = self.list_by_vendor(vendor)
            self.repo.generate_combined_orders_file(orders=orders)
            self.logger.info(f'Merge for {vendor} complete.')
        self.logger.info(f'Merging complete.')

        
@Logger.attach_logger
@dataclass(frozen=True)
class SaveOrder:
    repo: OrderRepository
    def __call__(self, order: Order) -> int:
        self.logger.info(f"Saving order {order.vendor} / {order.store} / {order.date}")
        return self.repo.save(order)

@Logger.attach_logger
@dataclass(frozen=True)
class ArchiveOrder:
    repo: OrderRepository
    def __call__(self, order: Order) -> int:
        self.logger.info(f"Archiving order {order.vendor} / {order.store} / {order.date}")
        return self.repo.archive_order(order)


@Logger.attach_logger
@dataclass(frozen=True)
class RemoveOrder:
    repo: OrderRepository
    def __call__(self, vendor: str, store: str, date: Optional[str] = None) -> None:
        self.logger.info(f"Removing order vendor={vendor}, store={store}, date={date}")
        self.repo.remove(vendor, store, date)


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
    get_order: GetOrdersByVendor
    gen_upload: GenerateVendorUploadFile

    def __call__(
        self,
        vendors: list[str],
        stores: Optional[List[str]] = None,
        start_date: Optional[str] = None,   # reserved for future repo filters
        end_date: Optional[str] = None,     # reserved for future repo filters
        context_map: dict[str, dict] | None = None
    ) -> list:
        outs = []
        
        for vendor in vendors:
            for store in stores:
                order = self.get_order(store, vendor)
                if not order: continue
                context = context_map.get(f'{order.store}|{order.vendor}')
                outs.append(self.gen_upload(order, context))
        return outs


# @Logger.attach_logger
# @dataclass(frozen=True)
# class ExpectDownloadedPdf:
#     """
#     Watches for one download and delegates ingesting it to the repository.
#     App layer doesn't compute paths or change suffixes.
#     """
#     repo: OrderRepository
#     downloads: DownloadPort

#     def __call__(self, order: Order, match: Optional[Callable] = None, timeout: int = 30) -> None:
#         self.logger.info(f"Expecting downloaded PDF for {order.vendor} / {order.store} / {order.date}")

#         # Default match rule if caller doesn't provide one
#         matcher = match or (lambda f: f.name.lower().endswith(".pdf"))

#         def handle(file_path):
#             # Delegate the storage/placement details to the repository.
#             self.repo.ingest_downloaded_attachment(order, src_path=file_path, kind="pdf")
#             self.logger.info(f"Ingested downloaded PDF: {file_path}")

#         self.downloads.on_download_once(match_fn=matcher, callback=handle, timeout=timeout)

@Logger.attach_logger
@dataclass(frozen=True)
class IngestDownloadedFile:

    repo: OrderRepository

    def __call__(self, order: Order, file_path: Path, kind: str = 'pdf') -> Path:

        self.repo.ingest_downloaded_attachment(
            order=order,
            src_path=file_path,
            kind=kind,
        )


    
# ========== DIFF / VALIDATION ==========

@Logger.attach_logger
@dataclass(frozen=True)
class CheckAndUpdateOrder:
    """
    Read it like a question.

    (Yes.) Returns True if no existing order or if it differs.
    (No.)  Returns False if an equivalent order already exists (no update needed).

    """
    repo: OrderRepository

    def __call__(self, order: Order) -> bool:

        try:
            existing = self.repo.get(order.store, order.vendor, date=order.date)
        except FileNotFoundError:
            self.logger.info("[Order Update] No existing order found for same vendor/store/date")
            return True
        except Exception as e:
            self.logger.warning(f"[Order Update] Failed to fetch existing order: {e}. Proceeding as changed.")
            return True
        
        same = _same(existing, order)
        self.logger.info("[Order Update] Unchanged - skip overwrite." if same else "[Order Update] Changed - overwrite needed.")

        return not same # Gross, but for semantic consistency

@Logger.attach_logger
@dataclass(frozen=True)
class GenerateStoreOrderEmail:

    repo: OrderRepository

    def __call__(self, store: str) -> None:
        pass
    
@Logger.attach_logger
@dataclass(frozen=True)
class GenerateStoreOrderEmails:

    repo: OrderRepository
    gen_email: GenerateStoreOrderEmail

    def __call__(self, stores: List[str]) -> None:
        pass

# ========== DOMAIN COMPARISON HELPERS ==========

def _same(a: Order, b: Order) -> bool:

    if (not a) or (not b): return False

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


@dataclass
class OrderServices:

    repo:      OrderRepository
    downloads: DownloadManagerPort

    def __post_init__(self) -> None:
        
        self.list_orders          = ListOrders(self.repo)
        self.get_orders_by_vendor = GetOrdersByVendor(self.repo)
        self.get_orders_by_store  = GetOrdersByStore(self.repo)
        self.get_order            = GetOrder(self.repo)
        self.get_orders           = GetOrders(self.repo, self.get_order)

        self.save_order     = SaveOrder(self.repo)
        self.remove_order   = RemoveOrder(self.repo)
        self.archive_order  = ArchiveOrder(self.repo)
        self.combine_orders = CombineOrders(self.repo, self.get_orders_by_vendor)

        self.generate_vendor_upload  = GenerateVendorUploadFile(self.repo)
        self.generate_vendor_uploads = GenerateVendorUploadFiles(
            self.get_order,
            self.generate_vendor_upload
        )

        self.ingest_downloaded_file = IngestDownloadedFile(self.repo)
        # self.expect_downloaded_pdf = ExpectDownloadedPdf(self.repo, self.downloads)
        self.check_and_update_order = CheckAndUpdateOrder(self.repo)

        self.generate_store_order_email = GenerateStoreOrderEmail(self.repo)
        self.generate_store_order_emails = GenerateStoreOrderEmails(self.repo, self.generate_store_order_email)
