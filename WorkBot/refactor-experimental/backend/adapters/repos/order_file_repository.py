from backend.app.ports import OrderRepository
from pathlib import Path

from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.order import OrderSerializer
from backend.domain.naming.order_namer import OrderFilenameStrategy
from backend.domain.models import Order
from backend.adapters.files.local_blob_store import LocalBlobStore

class OrderFileRepository(OrderRepository):
    """File-backed implementation of OrderRepository using GenericFileAdapter."""

    def __init__(self, base_dir: Path, uploads_dir: Path):
        self._engine = GenericFileAdapter[Order](
            store=LocalBlobStore(),
            serializer=OrderSerializer(),
            namer=OrderFilenameStrategy(orders_base_dir=base_dir, uploads_base_dir=uploads_dir),
        )

    # ---- Repository API ----
    def get_order(self, vendor: str, store: str, date: str | None = None) -> Order:
        """Get the current or specific dated order for vendor+store."""
        matches = self._engine.find(vendor=vendor, store=store)

        if date:
            matches = [o for o in matches if o.date == date]

        if not matches:
            raise FileNotFoundError(f"No order found for vendor={vendor}, store={store}, date={date}")

        # If no date: pick most recent
        matches.sort(key=lambda o: o.date, reverse=True)
        return matches[0]

    def list_orders(self) -> list[Order]:
        return [self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")]

    def list_by_vendor(self, vendor: str) -> list[Order]:
        return [o for o in self.list_all() if o.vendor == vendor]

    def list_by_store(self, store: str) -> list[Order]:
        return [o for o in self.list_all() if o.store == store]

    def save_order(self, order: Order) -> int:
        self._engine.save(order, format="xlsx")
        return 1

    def remove_order(self, vendor: str, store: str, date: str | None = None) -> None:
        try:
            order = self.get(vendor, store, date)
            path = self._engine.get_file_path(order, format="xlsx")
            self._engine.remove(path)
        except FileNotFoundError:
            pass

    def generate_vendor_upload_file(self, order: Order, context: dict | None = None) -> None:
        dest_path = self._engine.namer.upload_path_for(order)
        return self._engine.save(order, format=order.vendor, context=context, path_override=dest_path)
    