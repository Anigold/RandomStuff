from ..stores.Store import Store
from pathlib import Path
import re

class Order:

    def __init__(self, store: Store, vendor: str, date: str, items: list = []) -> None:
        self.store  = store
        self.vendor = vendor
        self.date   = date
        self.items  = items

    def load_items_from_csv(self, load_path: Path) -> None:
        pass

    def generate_item_csv(self, save_path: Path) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            'store': self.store,
            'vendor': self.vendor,
            'date': self.date,
            'items': self.items
        }

    def is_validate_date_format(self, given_date: str) -> bool:
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        return bool(date_pattern.match(given_date))