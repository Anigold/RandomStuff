from backend.app.ports import OrderRepository
from pathlib import Path
from typing import List
from collections import defaultdict

from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.order import OrderSerializer
from backend.domain.naming.order_namer import OrderFilenameStrategy
from backend.domain.models import Order
from backend.infra.filesystem.local_blob_store import LocalBlobStore
from backend.infra.logger import Logger

from backend.domain.models.orders.combine_orders import OrderCombiner

from pprint import pprint

@Logger.attach_logger
class OrderFileRepository(OrderRepository):
    """File-backed implementation of OrderRepository using GenericFileAdapter."""

    def __init__(self, base_dir: Path, uploads_dir: Path, archive_dir: Path):
        self._uploads_dir = uploads_dir
        self._engine = GenericFileAdapter[Order](
            store=LocalBlobStore(),
            serializer=OrderSerializer(),
            namer=OrderFilenameStrategy(
                orders_base_dir=base_dir,
                uploads_base_dir=uploads_dir, 
                archive_dir=archive_dir
            ),
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

    def save(self, order: Order) -> None:
        self._engine.save(order, format="xlsx")

    def save_data(self, data: bytes) -> None:
        self._engine.store.write_bytes()

    def archive_order(self, order: Order) -> None:
        # Should probably make this more dynamic for when order file type(s) change...
        
        order_file_path     = self._engine.get_file_path(order, format='xlsx')
        order_file_path_pdf = self._engine.get_file_path(order, format='pdf')

        archive_path_excel  = self._engine.get_file_path(order, format='xlsx', category='archive')
        archive_path_pdf    = self._engine.get_file_path(order, format='pdf', category='archive')

        self._engine.move(order_file_path, archive_path_excel, overwrite=True)
        self._engine.move(order_file_path_pdf, archive_path_pdf, overwrite=True)
        return

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

        Assumes all orders share a common vendor for file-saving name
        conventions (e.g. orders > vendor > combined_order.xlsx).

        Args:
            orders: List of Order objects across different stores.

        Returns:
            None
        """
        # combined = OrderCombiner.combine(orders)

        if not orders:
            raise ValueError("No orders provided for combination.")

        # ---- Step 1: collect all unique item names ----
        item_map: dict[str, dict[str, float]] = {}
        store_names = sorted({o.store for o in orders})

        headers = ['Item Name']
        headers.extend(store_names)

        for order in orders:

            store = order.store
            for item in order.items:

                if item.name not in item_map:
                    item_map[item.name] = {store: float(item.quantity)}
                    continue

                if store not in item_map[item.name]:
                    item_map[item.name][store] = float(item.quantity)
                    continue

        rows = []
        for item_name, quantities in sorted(item_map.items()):
           row = [item_name] + [quantities.get(store, '') for store in store_names]
           rows.append(row)

        output = {'headers': headers, 'rows': rows, 'metadata': {}}
        # self.logger.info(f'Combine orders output: {output}')
        excel_formatter = self._engine.serializer.get_formatter('xlsx')
        file_data = excel_formatter.dumps(output)

        # NEED TO REFACTOR THIS TO ENSURE FILE LOCATION AGNOSTICISM
        dest_path = (
            self._engine.namer.base_dir()
            / orders[0].vendor
            / f"combined_orders_{orders[0].vendor}.xlsx"
        ).resolve()
        self._engine.save_data(file_data, path_override=dest_path)
