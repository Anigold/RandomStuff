from WorkBot.refactor.backend.storage.file import item_file_handler
from backend.models.item import Item
from typing import Dict, List

class ItemCoordinator:
    def __init__(self, file_handler: item_file_handler):
        self.file_handler = file_handler
        self.items: Dict[str, Item] = {}

    def get_or_create_item(self, name: str) -> Item:
        if name not in self.items:
            self.items[name] = Item(name)
        return self.items[name]

    def add_vendor_data(self, vendor: str, vendor_item_data: Dict[str, dict]) -> None:
        for name, info in vendor_item_data.items():
            item = self.get_or_create_item(name)
            item.add_vendor_info(vendor, info)

    def add_store_quantity(self, store: str, item_name: str, quantity: float) -> None:
        item = self.get_or_create_item(item_name)
        item.add_store_info(store, quantity)

    def save_items(self) -> None:
        self.file_handler.save_items(self.items)

    def load_items(self) -> None:
        self.items = self.file_handler.load_items()

    def get_downloads_path(self) -> str:
        from config import DOWNLOADS_PATH
        return DOWNLOADS_PATH
