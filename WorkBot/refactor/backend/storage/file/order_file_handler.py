from config.paths import ORDER_FILES_DIR, UPLOAD_FILES_DIR
from backend.storage.file.file_handler import FileHandler
from backend.models.order import Order
from backend.serializer.formats import get_format, FORMATS
from backend.serializer.serializers.order_serializer import OrderSerializer
from backend.serializer.filename_strategies.order_filename_strategy import OrderFilenameStrategy
from backend.utils.logger import Logger
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from collections import defaultdict
from backend.serializer.adapters import get_adapter


@Logger.attach_logger
class OrderFileHandler(FileHandler):

    ORDER_FILES_DIR = Path(ORDER_FILES_DIR)
    VENDOR_UPLOAD_FILES_PATH = Path(UPLOAD_FILES_DIR)

    def __init__(self):
        super().__init__(self.ORDER_FILES_DIR)
        self.serializer        = OrderSerializer()
        self.filename_strategy = OrderFilenameStrategy()

    def save_order(self, order: Order, format: str = "excel") -> Path:
        headers   = self.serializer.get_headers()
        rows      = self.serializer.to_rows(order)
        formatter = get_format(format)
        data      = formatter.write(headers, rows)

        file_path = self.get_order_file_path(order, format)
        self._write_data(format, data, file_path)
        return file_path

    def get_order_from_file(self, file_path: Path) -> Order:
        ext       = file_path.suffix.lstrip(".").lower()
        formatter = get_format(ext)
        rows      = formatter.read(file_path)
        meta      = self.filename_strategy.parse(file_path.name)
        return self.serializer.from_rows(rows, metadata=meta)

    def get_order_file_path(self, order: Order, format: str = 'excel') -> Path:
        suffix = f".{self.extension_map.get(format, 'xlsx')}"
        filename = self.filename_strategy.format(order, extension=suffix.strip('.'))
        return self.ORDER_FILES_DIR / order.vendor / filename

    def get_upload_files_path(self, order: Order, format: str = 'excel') -> Path:
        suffix = f".{self.extension_map.get(format, 'xlsx')}"
        filename = self.filename_strategy.format(order, extension=suffix.strip('.'))
        return self.VENDOR_UPLOAD_FILES_PATH / order.vendor / filename

    def get_order_files(
        self,
        stores: list[str] | None,
        vendors: list[str] | None,
        start_date: str | None = None,
        end_date: str | None = None,
        formats: list[str] | None = ['xlsx'],       # e.g. ["pdf"] or ["excel","csv"]; None=all
    ) -> list[Path]:
        
        stores_set  = {s.strip().lower() for s in (stores or []) if s and s.strip()}
        vendors_set = {v.strip().lower() for v in (vendors or []) if v and v.strip()}
        want_all_vendors = len(vendors_set) == 0

        # Build allowed ext set
        if formats:  # names like "excel","csv","pdf"
            # extension_map may contain values like "xlsx","csv","pdf"
            ext_from_name = lambda name: self.extension_map.get(name.lower(), name).lower()
            allowed_exts = {ext_from_name(n).lstrip(".") for n in formats}
        else:
            allowed_exts = {ext.lower().lstrip(".") for ext in self.extension_map.values()}

        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end   = datetime.strptime(end_date,   "%Y-%m-%d") if end_date   else None

        def matches_filters(meta: dict) -> bool:
            if not meta or "date" not in meta:
                return False
            if stores_set and (meta.get("store","").strip().lower() not in stores_set):
                return False
            try:
                file_date = datetime.strptime(meta["date"], "%Y-%m-%d")
            except Exception:
                return False
            if start and file_date < start: return False
            if end   and file_date > end:   return False
            return True

        matched: list[Path] = []
        for vendor_dir in self.ORDER_FILES_DIR.iterdir():
            if not vendor_dir.is_dir():
                continue
            if not want_all_vendors and vendor_dir.name.strip().lower() not in vendors_set:
                continue

            for file in vendor_dir.iterdir():
                if not file.is_file():
                    continue
                suffix = file.suffix.lower().lstrip(".")  # ".XLSX" -> "xlsx"
                if suffix not in allowed_exts:
                    continue
                meta = self.filename_strategy.parse(file.name)
                if matches_filters(meta):
                    matched.append(file)

        matched.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
        return matched
    
    def get_order_directory(self) -> Path:
        return self.ORDER_FILES_DIR

    def archive_order_file(self, order: Order) -> None:
        vendor_dir = self.ORDER_FILES_DIR / order.vendor
        archive_dir = vendor_dir / "CompletedOrders"
        archive_dir.mkdir(parents=True, exist_ok=True)

        filename_prefix = self.filename_strategy.prefix(order)

        for file in vendor_dir.iterdir():
            if not file.is_file() or not file.name.startswith(filename_prefix):
                continue

            dest = archive_dir / file.name
            try:
                self.move_file(file, dest, overwrite=True)
                self.logger.info(f"Archived order file: {file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to archive {file.name}: {e}")

    def combine_orders_by_store(self, vendors: list[str]) -> None:
        for vendor in vendors:
            order_paths = self.get_order_files(stores=[], vendors=[vendor])
            if not order_paths:
                continue
            orders = [self.get_order_from_file(p) for p in order_paths]

            combined = defaultdict(lambda: defaultdict(float))
            for order in orders:
                store = order.store.upper()
                for item in order.items:
                    combined[item.name][store] += float(item.quantity)

            workbook = self._create_combined_orders_excel(combined)
            output_path = self.get_order_directory() / vendor / "combined_orders.xlsx"
            self._write_data("excel", workbook, output_path)
    
    def generate_vendor_upload_file(self, order: Order, context: dict | None = None) -> Path:
        """Serialize an order for a vendor and persist it using the vendor's preferred format."""
        ctx = context or {}

        # 1) Resolve adapter (vendor-specific tweaks) and formatter (csv/excel)
        adapter = get_adapter(order.vendor)
        if not adapter:
            self.logger.error(f"[upload] Unknown vendor: {order.vendor}")
            raise ValueError(f"Unknown vendor: {order.vendor}")

        fmt_name  = getattr(adapter, "preferred_format", "excel").lower()
        formatter = get_format(fmt_name)  # ABC-backed instance

        # 2) Produce tabular data (serializer -> headers/rows), then let adapter tweak
        headers = self.serializer.get_headers()
        headers = adapter.modify_headers(headers, context=ctx)

        base_rows = self.serializer.to_rows(order)
        # rows = [adapter.modify_row(r, context=ctx) for r in base_rows]
        rows = []
        for row, item in zip(base_rows, order.items):
            try:
                rows.append(adapter.modify_row(row, item=item, context=ctx))
            except TypeError:
                rows.append(adapter.modify_row(row, item=item))

        # Optional sanity check (keeps bugs obvious)
        if not isinstance(headers, list) or any(not isinstance(r, list) for r in rows):
            self.logger.error(f"[upload] Bad tabular output for {order.vendor}: headers/rows malformed")
            raise ValueError("Serializer/adapter produced malformed tabular data")

        # 3) Render via formatter
        file_data = formatter.write(headers, rows)
        
        # 4) Build output path using formatter’s primary extension
        # ext = (formatter.extensions[0] if getattr(formatter, "extensions", ()) else ".xlsx").lstrip(".")
        output_path = self.get_upload_files_path(order, format=fmt_name)  # uses fmt_name -> ext internally
        # If your path builder expects an extension string instead of a name:
        # output_path = self.get_upload_files_path(order, format=ext)

        # 5) Persist
        self._write_data(fmt_name, file_data, output_path)

        self.logger.info(f"[upload] {order.vendor} | {order.store} | {order.date} -> {output_path}")
        return output_path
 
    def generate_vendor_upload_files(
        self,
        orders: list[Order],
        context_map: dict[str, dict] = None,
    ) -> list[Path]:
        results: list[Path] = []
        for order in orders:
            print(order, flush=True)
            # Use a stable domain key if you prefer (vendor|store|date); keeping path-prekey for now.
            fmt         = self._peek_preferred_format(order)
            prekey_path = self.get_upload_files_path(order, format=fmt)
            ctx         = (context_map or {}).get(str(prekey_path), {})
            results.append(self.generate_vendor_upload_file(order, context=ctx))
        return results
    
    def _peek_preferred_format(self, order: Order) -> str:
        adapter = BaseAdapter.get_adapter(order.vendor)
        return getattr(adapter, "preferred_format", "excel").lower() if adapter else "excel"

    def parse_filename_for_metadata(self, file_name: str) -> dict:
        return self.filename_strategy.parse(filename=file_name)
        
    def _generate_filename(self, order: Order, format: str) -> str:
        formatter = get_format(format)
        suffix = self.extension_map.get(format, 'xlsx')
        filename = self.filename_strategy.format(order, extension=suffix.lstrip('.'))
        return filename
    
    def _create_combined_orders_excel(self, combined_orders: dict[str, dict[str, float]]) -> Workbook:
        workbook = Workbook()
        sheet = workbook.active

        store_names = sorted({store for stores in combined_orders.values() for store in stores})
        headers = ['Item'] + store_names
        sheet.append(headers)

        for item_name, store_quantities in sorted(combined_orders.items()):
            row = [item_name] + [store_quantities.get(store, '') for store in store_names]
            sheet.append(row)

        return workbook
