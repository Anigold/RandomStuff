from Store import Store
import json

class StoreManager:

    def __init__(self):
        self.stores = {}

    def add_store(self, store_id: int, name: str):
        """Add a new store and save it."""
        if store_id in self.stores:
            print(f"Store ID {store_id} already exists.")
            return
        self.stores[store_id] = Store(store_id, name)
        self.save_stores()

    def get_store(self, store_id: int):
        """Retrieve a store by ID."""
        return self.stores.get(store_id)

    def save_stores(self):
        """Save all stores to a JSON file."""
        with open(self.storage_file, "w") as f:
            json.dump({sid: store.to_dict() for sid, store in self.stores.items()}, f, indent=4)

    def load_stores(self):
        """Load stores from a JSON file."""
        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                self.stores = {int(sid): Store.from_dict(store_data) for sid, store_data in data.items()}
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
