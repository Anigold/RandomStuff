from config.paths import ORDER_FILES_DIR, UPLOAD_FILES_DIR
from backend.storage.file.file_handler import FileHandler
from backend.models.order import Order
from backend.parsers.order_parser import OrderParser
from pathlib import Path
from openpyxl import Workbook
from typing import Any
from backend.exporters.excel_exporter import Exporter
from backend.storage.file.helpers.filename_strategies.order_filename_strategy import OrderFilenameStrategy
from backend.utils.logger import Logger
from datetime import datetime
from collections import defaultdict

@Logger.attach_logger
class OrderFileHandler(FileHandler):
    
    ORDER_FILES_DIR = Path(ORDER_FILES_DIR)
    VENDOR_UPLOAD_FILES_PATH = Path(UPLOAD_FILES_DIR)

    def __init__(self):
        super().__init__(self.ORDER_FILES_DIR)
        self.parser = OrderParser()
        self.filename_strategy = OrderFilenameStrategy()
        
    def _generate_file_name(self, order: Order, format: str) -> str:
        ext = self.extension_map.get(format, 'excel')
        return self.filename_strategy.format(order, extension=ext)
        
    def save_order(self, order: Order, format: str) -> None:
        exporter  = Exporter.get_exporter(Order, format)
        file_data = exporter.export(order)
        file_name = self._generate_file_name(order, format)
        file_path = self.ORDER_FILES_DIR / order.vendor / file_name
        self._write_data(format, file_data, file_path)

    def get_order_files(
            self, 
            stores: list[str], 
            vendors: list[str], 
            start_date: str = None, 
            end_date: str = None
        ) -> list[Path]:
        """
        Returns all order files whose parsed metadata falls within the given vendor, store, and date range filters.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end   = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        def matches_filters(meta: dict) -> bool:
            if not meta or "date" not in meta:
                return False
            if stores and meta.get("store") not in stores:
                return False
            if start or end:
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
            if not vendor_dir.is_dir():
                continue
            if vendors and vendor_dir.name not in vendors:
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
    
    def get_order_file_path(self, order: Order, format: str = 'excel') -> Path:
        return self.ORDER_FILES_DIR / order.vendor / self._generate_file_name(order, format)

    def read_order(self, file_path: Path) -> Order:
        return self.parser.parse_excel(file_path)
    
    def get_upload_files_path(self, order: Order, format: str = 'excel') -> Path:
        return self.VENDOR_UPLOAD_FILES_PATH / order.vendor / self._generate_file_name(order, format=format)

    def archive_order_file(self, order: Order) -> None:
        """
        Moves all files related to the given order into the vendor's CompletedOrders archive folder.
        Matches based on filename prefix (vendor_store_date). Overwrites files in the archive if they already exist.
        """
        vendor_dir = self.ORDER_FILES_DIR / order.vendor
        archive_dir = vendor_dir / "CompletedOrders"
        archive_dir.mkdir(parents=True, exist_ok=True)

        filename_prefix = self.filename_strategy.prefix(order)

        for file in vendor_dir.iterdir():
            if not file.is_file() or not file.name.startswith(filename_prefix):
                continue

            dest = archive_dir / file.name
            try:
                if dest.exists():
                    dest.unlink()  # Remove the existing file to allow overwrite
                file.rename(dest)
                self.logger.info(f"Archived order file: {file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to archive {file.name}: {e}")

    def combine_orders_by_store(self, vendors: list[str]) -> None:
        
        for vendor in vendors:
            order_paths = self.get_order_files(stores=[], vendors=[vendor])

            if not order_paths:
                continue

            orders = [self.read_order(p) for p in order_paths]
            
            combined = defaultdict(lambda: defaultdict(float))
            for order in orders:
                store = order.store.upper()
                for item in order.items:
                    combined[item.name][store] += float(item.quantity)

            workbook = self._create_combined_orders_excel(combined)
            output_path = self.get_order_directory() / vendor / "combined_orders.xlsx"
            self._write_data('excel', workbook, output_path)

    def _create_combined_orders_excel(self, combined_orders: dict[str, dict[str, float]]) -> Workbook:
        """
        Constructs a workbook from combined order data.
        Format: Item | STORE_A | STORE_B | ...
        """
        workbook = Workbook()
        sheet = workbook.active

        # Dynamically extract and sort store names
        store_names = sorted({store for stores in combined_orders.values() for store in stores})
        headers = ['Item'] + store_names
        sheet.append(headers)

        # Write each row
        for item_name, store_quantities in sorted(combined_orders.items()):
            row = [item_name] + [store_quantities.get(store, '') for store in store_names]
            sheet.append(row)

        return workbook