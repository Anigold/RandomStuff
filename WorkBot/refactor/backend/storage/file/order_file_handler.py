from config.paths import ORDER_FILES_DIR, UPLOAD_FILES_DIR
from backend.storage.file.file_handler import FileHandler
from backend.models.order import Order
from backend.serializer.formats.excel_format import ExcelFormat
from backend.serializer.serializers.order_serializer import OrderSerializer
from backend.serializer.filename_strategies.order_filename_strategy import OrderFilenameStrategy
from backend.utils.logger import Logger
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from collections import defaultdict

@Logger.attach_logger
class OrderFileHandler(FileHandler):

    ORDER_FILES_DIR = Path(ORDER_FILES_DIR)
    VENDOR_UPLOAD_FILES_PATH = Path(UPLOAD_FILES_DIR)

    def __init__(self):
        super().__init__(self.ORDER_FILES_DIR)
        self.serializer = OrderSerializer()
        self.format = ExcelFormat()
        self.filename_strategy = OrderFilenameStrategy()

    def save_order(self, order: Order, format: str = "excel") -> Path:
        headers = self.serializer.get_headers()
        rows = self.serializer.to_rows(order)
        data = self.format.write(headers, rows)

        file_path = self.get_order_file_path(order, format)
        self._write_data(format, data, file_path)
        return file_path

    def get_order_from_file(self, file_path: Path) -> Order:
        rows = self.format.read(file_path)
        meta = self.filename_strategy.parse(file_path.name)
        return self.serializer.from_rows(rows, metadata=meta)

    def get_order_file_path(self, order: Order, format: str = 'excel') -> Path:
        suffix = f".{self.extension_map.get(format, 'xlsx')}"
        filename = self.filename_strategy.format(order, extension=suffix.strip('.'))
        return self.ORDER_FILES_DIR / order.vendor / filename

    def get_upload_files_path(self, order: Order, format: str = 'excel') -> Path:
        suffix = f".{self.extension_map.get(format, 'xlsx')}"
        filename = self.filename_strategy.format(order, extension=suffix.strip('.'))
        return self.VENDOR_UPLOAD_FILES_PATH / order.vendor / filename

    def get_order_files(self, stores: list[str], vendors: list[str], start_date: str = None, end_date: str = None) -> list[Path]:
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end   = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        def matches_filters(meta: dict) -> bool:
            if not meta or "date" not in meta:
                return False
            if stores and meta.get("store") not in stores:
                return False
            try:
                file_date = datetime.strptime(meta["date"], "%Y-%m-%d")
            except ValueError:
                return False
            if start and file_date < start:
                return False
            if end and file_date > end:
                return False
            return True

        matched_files = []
        for vendor_dir in self.ORDER_FILES_DIR.iterdir():
            if not vendor_dir.is_dir() or (vendors and vendor_dir.name not in vendors):
                continue
            for file in vendor_dir.iterdir():
                if not file.is_file() or file.suffix != '.xlsx':
                    continue
                meta = self.filename_strategy.parse(file.name)
                if matches_filters(meta):
                    matched_files.append(file)

        return matched_files

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

    def _generate_filename(self, order: Order, format: str) -> str:
        return self.filename_strategy.format(order, extension=self.extension_map.get(format, 'excel'))
    
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
