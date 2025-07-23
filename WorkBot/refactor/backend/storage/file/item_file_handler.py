from typing import Dict
from backend.models.item import Item, VendorItemInfo, StoreItemInfo
from config.paths import ITEMS_DATA_FILE
from backend.storage.file.file_handler import FileHandler

class ItemFileHandler(FileHandler):
    def __init__(self, file_path=ITEMS_DATA_FILE):
        super().__init__(file_path)

    def save_items(self, items: Dict[str, Item]) -> None:
        data = {name: item.to_dict() for name, item in items.items()}
        self.write_json(self.base_path, data)

    def load_items(self) -> Dict[str, Item]:
        data = self.read_json(self.base_path)
        items: Dict[str, Item] = {}
        for name, item_data in data.items():
            item = Item(name=item_data["name"], item_id=item_data["id"])

            for vendor, infos in item_data.get("vendors", {}).items():
                for info in infos:
                    item.add_vendor_info(vendor, VendorItemInfo(**info))

            for store, info in item_data.get("stores", {}).items():
                item.add_store_info(store, StoreItemInfo(**info))

            items[name] = item
        return items
