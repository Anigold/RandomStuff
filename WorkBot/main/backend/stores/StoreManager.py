from .Store import Store
import json
from pathlib import Path
from config.paths import STORES_DATA_FILE
from pprint import pprint

class StoreManager:

    def __init__(self, storage_file: Path):
        self.stores = {}
        self.storage_file = storage_file or STORES_DATA_FILE
        self.load_stores()

    def add_store(self, store_id: int, name: str) -> None:
        """Add a new store and save it."""
        if store_id in self.stores:
            print(f"Store ID {store_id} already exists.")
            return
        self.stores[store_id] = Store(store_id, name)
        self.save_stores()

    def get_store(self, store_id: int) -> Store:
        """Retrieve a store by ID."""
        return self.stores.get(store_id)

    def find_store_by_name(self, store_name: str) -> Store:
        """Retrieve a store by its name. 
        If more than one exists, return the first instance.
        """
        for store in self.list_stores():
            if store.name == store_name:
                return self.get_store(store.store_id)
        
    def save_stores(self):
        """Save all stores to a JSON file."""
        with open(self.storage_file, "w") as f:
            json.dump({sid: store.to_dict() for sid, store in self.stores.items()}, f, indent=4)

    def load_stores(self):
        """Load stores from a JSON file."""
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.stores = {sid: Store.from_dict(store_data) for sid, store_data in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            self.stores = {}

    def remove_store(self, store_id: int):
        """Remove a store by ID."""
        if store_id in self.stores:
            del self.stores[store_id]
            self.save_stores()

    def list_stores(self):
        """Return a list of all stores."""
        return list(self.stores.values())
    
    def __repr__(self) -> str:
        return f'StoreManager({self.stores}, {self.storage_file})'
