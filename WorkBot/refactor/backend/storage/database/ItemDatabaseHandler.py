from backend.storage.database.DatabaseHandler import DatabaseHandler
from backend.models.Item import Item
from backend.models.VendorItemInfo import VendorItemInfo
from backend.models.StoreItemInfo import StoreItemInfo
from typing import Dict, List


class ItemDatabaseHandler(DatabaseHandler):
    """Handles database operations related to items, including fetching, inserting,
    and updating item information along with their vendor and store details."""

    def get_items(self) -> Dict[str, Item]:
        """Fetch all items and their vendor/store info from the database."""
        items = {}

        item_rows = self.fetch_all("SELECT id, item_name FROM items")
        for item_id, name in item_rows:
            item = Item(name=name, id=item_id)
            items[name] = item

        # Step 2: Add vendor info
        vendor_rows = self.fetch_all(
            "SELECT item_id, vendor_id, vendor_sku, units_id, price, case_size FROM VendorItems"
        )

        if vendor_rows:
            for row in vendor_rows:
                for item in items.values():
                    if item.id == row["item_id"]:
                        vi = VendorItemInfo(
                            sku=row["sku"],
                            unit=row["unit"],
                            quantity=row["quantity"],
                            cost=row["cost"],
                            case_size=row["case_size"]
                        )
                        item.add_vendor_info(row["vendor"], vi)
                        break

                store_rows = self.fetch_all("""
                    SELECT item_id, store_id, on_hand
                    FROM StoreItems
                """)
                for row in store_rows:
                    item_id, store, quantity_on_hand = row
                    item = next((i for i in items.values() if i.id == item_id), None)
                    if item:
                        item.add_store_info(store, StoreItemInfo(quantity_on_hand))

                return items

    # def insert_or_update_item(self, item: Item) -> None:
    #     self.execute(
    #         "INSERT OR IGNORE INTO items (id, item_name) VALUES (?, ?)",
    #         (item.id, item.name)
    #     )
    #     for vendor, infos in item.vendor_info.items():
    #         for vi in infos:
    #             self.execute(
    #                 """INSERT INTO vendor_items (item_id, vendor, sku, unit, quantity, cost, case_size)
    #                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
    #                 (item.id, vendor, vi.sku, vi.unit, vi.quantity, vi.cost, vi.case_size)
    #             )

    #     for store, si in item.store_info.items():
    #         self.execute(
    #             """INSERT OR REPLACE INTO store_items (item_id, store, quantity_on_hand)
    #                VALUES (?, ?, ?)""",
    #             (item.id, store, si.quantity_on_hand)
    #         )

    # def clear_all_items(self) -> None:
    #     """Useful for full refresh."""
    #     self.execute("DELETE FROM vendor_items")
    #     self.execute("DELETE FROM store_items")
    #     self.execute("DELETE FROM items")
