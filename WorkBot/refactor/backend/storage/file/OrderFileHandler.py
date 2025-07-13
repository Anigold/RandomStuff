# backend/ordering/storage/order_file_handler.py

from config.paths import ORDER_FILES_DIR
from backend.storage.file_handler import FileHandler
from models.Order import Order
from parsers.OrderParser import OrderParser
from pathlib import Path
import re


class OrderFileHandler(FileHandler):
    file_pattern = re.compile(r"^(?P<vendor>.+?)_(?P<store>.+?)_(?P<date>\d{8})")

    def __init__(self, base_dir=ORDER_FILES_DIR):
        super().__init__(base_dir)
        self.parser = OrderParser()

    def save_order(self, order: Order):
        path = self.get_order_path(order)
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook = order.to_excel_workbook()
        workbook.save(path)

    def get_order_path(self, order: Order) -> Path:
        filename = f"{order.vendor}_{order.store}_{order.date}.xlsx"
        return self.base_path / order.vendor / filename

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
