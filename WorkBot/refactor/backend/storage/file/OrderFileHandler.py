from config.paths import ORDER_FILES_PATH
from backend.storage.file.FileHandler import FileHandler
from backend.models.Order import Order
from backend.parsers.OrderParser import OrderParser
from pathlib import Path
import re
from openpyxl import Workbook
from typing import Any
from backend.exporters import get_exporter

class OrderFileHandler(FileHandler):
    file_pattern = re.compile(r"^(?P<vendor>.+?)_(?P<store>.+?)_(?P<date>\d{8})")
    order_files_path = Path(ORDER_FILES_PATH)
    
    def __init__(self, base_dir=ORDER_FILES_PATH):
        super().__init__(base_dir)
        self.parser = OrderParser()
        
    def _generate_file_name(self, order: Order, format: str) -> str:
        ext = self.extension_map.get(format, 'xlsx')
        return f'{order.vendor}_{order.store}_{order.date}.{ext}'
    
    def save_order(self, order: Order, format: str) -> None:

        exporter = get_exporter(Order, format)
        file_data_to_save = exporter.export(order)

        file_name = self._generate_file_name(order, format)

        self._write_data(format, file_data_to_save, ORDER_FILES_PATH / file_name)

    def _write_data(self, format: str, data: Any, file_path: Path) -> None:
        try:
            save_func = self._save_strategies[format]
        except KeyError:
            raise ValueError(f"Unsupported format: {format}")
        save_func(data, file_path)

    # def get_order_path(self, order: Order) -> Path:
    #     filename = f"{order.vendor}_{order.store}_{order.date}.xlsx"
    #     return self.base_path / order.vendor / filename

    def get_orders(self, stores: list = None, vendors: list = None):
        orders = []
        for vendor_dir in self.base_path.iterdir():
            if not vendor_dir.is_dir():
                continue
            if vendors and vendor_dir.name not in vendors:
                continue
            for file in vendor_dir.glob("*.xlsx"):
                meta = self.parse_filename(file.name)
                if stores and meta.get('store') not in stores:
                    continue
                orders.append(self.parser.parse_excel(file))
        return orders

    def parse_filename(self, filename: str) -> dict:
        match = self.file_pattern.match(Path(filename).stem)
        return match.groupdict() if match else {}
    