from ..stores.Store import Store
from pathlib import Path


class Order:

    def __init__(self, store: Store, vendor: str, date: str, items: list = []) -> None:
        self.store  = store
        self.vendor = vendor
        self.date   = date
        self.items  = items
        
    def load_items_from_file(self, load_path: Path) -> None:
        pass

    def generate_item_file(self, save_path: Path) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            'store': self.store,
            'vendor': self.vendor,
            'date': self.date,
            'items': self.items
        }
    
