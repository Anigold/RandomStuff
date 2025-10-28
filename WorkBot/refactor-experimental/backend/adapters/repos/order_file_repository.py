from backend.app.ports import OrderRepository
from pathlib import Path
from typing import List
from collections import defaultdict

from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.order import OrderSerializer
from backend.domain.naming.order_namer import OrderFilenameStrategy
from backend.domain.models import Order
from backend.adapters.files.local_blob_store import LocalBlobStore
from backend.infra.logger import Logger

from backend.domain.models.orders.combine_orders import OrderCombiner

from pprint import pprint

@Logger.attach_logger
class OrderFileRepository(OrderRepository):
    """File-backed implementation of OrderRepository using GenericFileAdapter."""

    def __init__(self, base_dir: Path, uploads_dir: Path):
        self._uploads_dir = uploads_dir
        self._engine = GenericFileAdapter[Order](
            store=LocalBlobStore(),
            serializer=OrderSerializer(),
            namer=OrderFilenameStrategy(orders_base_dir=base_dir, uploads_base_dir=uploads_dir),
        )

    # ---- Repository API ----
    def get(self, store: str, vendor: str, date: str | None = None) -> Order:
        """Get the current or specific dated order for vendor+store."""
        matches = self._engine.find(store=store, vendor=vendor)
        return matches[0] if len(matches) >= 1 else None

    def list_all(self) -> list[Order]:
        return [self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")]

    def list_by_vendor(self, vendor: str) -> list[Order]:
        return [o for o in self.list_all() if o.vendor == vendor]

    def list_by_store(self, store: str) -> list[Order]:
        return [o for o in self.list_all() if o.store == store]

    def save(self, order: Order) -> int:
        self._engine.save(order, format="xlsx")
        return 1

    def remove(self, vendor: str, store: str, date: str | None = None) -> None:
        try:
            order = self.get(vendor, store, date)
            path = self._engine.get_file_path(order, format="xlsx")
            self._engine.remove(path)
        except FileNotFoundError:
            pass

    def generate_vendor_upload_file(self, order: Order, context: dict | None = None) -> None:
        formatter = self._engine.serializer.get_formatter(order.vendor.strip().lower())
        dest_path = self._engine.get_file_path(order, format=formatter.format_name(), category='upload')
        return self._engine.save(order, format=order.vendor, context=context, path_override=dest_path)
    
    def ingest_downloaded_attachment(self, order: Order, src_path: Path, kind: str) -> None:
        dest_path = self._engine.get_file_path(order, format=kind)
        self._engine.ensure_dir(dest_path.parent)
        self._engine.move(src_path, dest_path, overwrite=True)
        return dest_path
    
    def generate_combined_orders_file(self, orders: List[Order]) -> None:
        """
        Create a combined Excel sheet showing item quantities by store.

        Args:
            orders: List of Order objects across different stores.
            dest_path: Optional output path. If None, a timestamped file is created.

        Returns:
            Path to the created Excel file.
        """
        combined = OrderCombiner.combine(orders)

        if not orders:
            raise ValueError("No orders provided for combination.")

        # ---- Step 1: collect all unique item names ----
        item_map: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        store_names = sorted({o.store for o in orders})

        for order in orders:
            for item in order.items:
                item_map[item.name][order.store] += float(item.quantity)

        rows = []
        for item_name, quantities in sorted(item_map.items()):
           row = [item_name] + [quantities.get(store, 0) for store in store_names]
           rows.append(row)

      

        # ---- Step 2: prepare workbook ----
        # wb = Workbook()
        # ws = wb.active
        # ws.title = "Combined Orders"

        # # ---- Step 3: write headers ----
        # headers = ["Item Name"] + store_names
        # ws.append(headers)

        # # ---- Step 4: write rows ----
        # for item_name, quantities in sorted(item_map.items()):
        #     row = [item_name] + [quantities.get(store, 0) for store in store_names]
        #     ws.append(row)

        # # ---- Step 5: adjust column widths ----
        # for col_idx, header in enumerate(headers, start=1):
        #     column_letter = get_column_letter(col_idx)
        #     ws.column_dimensions[column_letter].width = max(12, len(header) + 2)

        # # ---- Step 6: determine destination path ----
        # if dest_path is None:
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     dest_path = self.base_dir / f"combined_orders_{timestamp}.xlsx"

        # # ---- Step 7: ensure directory exists ----
        # dest_path.parent.mkdir(parents=True, exist_ok=True)

        # # ---- Step 8: save workbook ----
        # wb.save(dest_path)
        # return dest_path


        
