from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from backend.domain.models import Order, Vendor, Store
from backend.app.ports import OrderRepository, VendorRepository, StoreRepository
from backend.infra.logger import Logger


@Logger.attach_logger
@dataclass
class FileLocator:
    """
    Minimal read-only utility for resolving file paths
    across domain repositories.

    Purpose:
      - Keep file-system logic out of higher-level services.
      - Avoid cross-domain repo coupling (like in EmailServices).
      - Provide a stable interface for locating files.

    This class does NOT read or write files — it only resolves paths.
    """

    orders_repo: OrderRepository
    vendors_repo: VendorRepository | None = None
    stores_repo: StoreRepository | None = None

    # ------------------------------------------------------------------
    # ---- Order Files -------------------------------------------------
    # ------------------------------------------------------------------
    def order_path(self, order: Order, format: str = "xlsx") -> Path:
        """Return the path where an order file lives or will be saved."""
        path = self.orders_repo._engine.get_file_path(order, format=format)
        self.logger.debug(f"Resolved path for order {order.vendor}/{order.store}: {path}")
        return path

    # ------------------------------------------------------------------
    # ---- Vendor / Store Files (Optional) ------------------------------
    # ------------------------------------------------------------------
    def vendor_path(self, vendor: Vendor, format: str = "json") -> Path:
        if not self.vendors_repo:
            raise RuntimeError("Vendor repository not configured for FileLocator.")
        path = self.vendors_repo.namer.path_for(vendor, format=format)
        self.logger.debug(f"Resolved path for vendor {vendor.name}: {path}")
        return path

    def store_path(self, store: Store, format: str = "json") -> Path:
        if not self.stores_repo:
            raise RuntimeError("Store repository not configured for FileLocator.")
        path = self.stores_repo.namer.path_for(store, format=format)
        self.logger.debug(f"Resolved path for store {store.name}: {path}")
        return path
