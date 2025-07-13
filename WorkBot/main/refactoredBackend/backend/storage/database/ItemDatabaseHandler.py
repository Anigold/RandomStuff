from backend.database.database_handler import DatabaseHandler
from backend.items.models.item import Item, VendorItemInfo, StoreItemInfo

from typing import Dict, List


class ItemDatabaseHandler(DatabaseHandler):
    def fetch_all_items(self) -> Dict[str, Item]:
        """Fetch all items and their vendor/store info from the database."""
        items = {}

        item_rows = self.fetchall("SELECT id, name FROM items")
        for item_id, name in item_rows:
            item = Item(name=name, item_id=item_id)
            items[name] = item

        vendor_rows = self.fetchall("""
            SELECT item_id, vendor, sku, unit, quantity, cost, case_size
            FROM vendor_items
        """)
        for row in vendor_rows:
            item_id, vendor, sku, unit, quantity, cost, case_size = row
            item = next((i for i in items.values() if i.id == item_id), None)
            if item:
                item.add_vendor_info(vendor, VendorItemInfo(sku, unit, quantity, cost, case_size))

        store_rows = self.fetchall("""
            SELECT item_id, store, quantity_on_hand
            FROM store_items
        """)
        for row in store_rows:
            item_id, store, quantity_on_hand = row
            item = next((i for i in items.values() if i.id == item_id), None)
            if item:
                item.add_store_info(store, StoreItemInfo(quantity_on_hand))

        return items

    def insert_or_update_item(self, item: Item) -> None:
        self.execute(
            "INSERT OR IGNORE INTO items (id, name) VALUES (?, ?)",
            (item.id, item.name)
        )
        for vendor, infos in item.vendor_info.items():
            for vi in infos:
                self.execute(
                    """INSERT INTO vendor_items (item_id, vendor, sku, unit, quantity, cost, case_size)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item.id, vendor, vi.sku, vi.unit, vi.quantity, vi.cost, vi.case_size)
                )

        for store, si in item.store_info.items():
            self.execute(
                """INSERT OR REPLACE INTO store_items (item_id, store, quantity_on_hand)
                   VALUES (?, ?, ?)""",
                (item.id, store, si.quantity_on_hand)
            )

    def clear_all_items(self) -> None:
        """Useful for full refresh."""
        self.execute("DELETE FROM vendor_items")
        self.execute("DELETE FROM store_items")
        self.execute("DELETE FROM items")
