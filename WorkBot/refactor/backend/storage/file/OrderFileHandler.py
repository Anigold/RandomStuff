from config.paths import ORDER_FILES_PATH
from backend.storage.file.FileHandler import FileHandler
from backend.models.Order import Order
from backend.parsers.OrderParser import OrderParser
from pathlib import Path
import re
from openpyxl import Workbook
from typing import Any
from backend.exporters.ExcelExporter import Exporter
from backend.storage.file.helpers.filename_strategies.order_filename_strategy import OrderFilenameStrategy
from backend.utils.logger import Logger


@Logger.attach_logger
class OrderFileHandler(FileHandler):
    
    BASE_DIR = Path(ORDER_FILES_PATH)
    
    def __init__(self):
        super().__init__(self.BASE_DIR)
        self.parser = OrderParser()
        self.filename_strategy = OrderFilenameStrategy()
        
    def _generate_file_name(self, order: Order, format: str) -> str:
        ext = self.extension_map.get(format, 'excel')
        return self.filename_strategy.format(order, extension=ext)
        
    def save_order(self, order: Order, format: str) -> None:

        exporter = Exporter.get_exporter(Order, format)
        file_data_to_save = exporter.export(order)

        file_name = self._generate_file_name(order, format)

        self._write_data(format, file_data_to_save, self.BASE_DIR / order.vendor / file_name)

    def _write_data(self, format: str, data: Any, file_path: Path) -> None:
        try:
            save_func = self._save_strategies[format]
        except KeyError:
            raise ValueError(f"Unsupported format: {format}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
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
    
    def get_order_file_path(self, order: Order, format: str = 'excel') -> Path:
        return self.base_dir / order.vendor / self._generate_file_name(order, format)

    def read_order(self, file_path: Path) -> Order:
        return self.parser.parse_excel(file_path)