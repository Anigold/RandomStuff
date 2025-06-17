from items.Item import Item
from config.paths import ITEMS_DATA_FILE
from pathlib import Path
import json

class ItemManager:

    def __init__(self, storage_file: Path):
        self.storage_file = storage_file or ITEMS_DATA_FILE
        self.items = self.load_items()

    def load_items(self) -> None:
        """Load stores from a JSON file."""
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.stores = {sid: Item.from_dict(store_data) for sid, store_data in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self.stores = {}


    def save_to_file(self, path: str | Path) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)
