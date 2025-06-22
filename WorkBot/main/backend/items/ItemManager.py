from items.Item import Item
from config.paths import ITEMS_DATA_FILE
from pathlib import Path
import json
from typing import Dict, List, Optional, Union
from items.Item import VendorItemInfo, StoreItemInfo

class ItemManager:
    """
    Manages all items, including cross-vendor and cross-store relationships,
    and handles JSON persistence.

    Attributes:
        items (Dict[str, Item]): Maps item names to Item instances.
    """

    def __init__(self):
        self.items: Dict[str, Item] = {}

    def get_or_create_item(self, item_name: str) -> Item:
        """
        Return an existing Item by name or create a new one if not found.
        """
        if item_name not in self.items:
            self.items[item_name] = Item(item_name)
        return self.items[item_name]

    def add_vendor_data(self, vendor: str, vendor_item_data: Dict[str, dict]) -> None:
        """
        Add pricing and SKU information from a vendor's product sheet.

        Args:
            vendor (str): Name of the vendor.
            vendor_item_data (Dict[str, dict]): Dict of item_name -> {SKU, units, quantity, cost, case_size}
        """
        for name, info in vendor_item_data.items():
            item = self.get_or_create_item(name)
            vendor_info = VendorItemInfo(
                sku=info["SKU"],
                unit=info["units"],
                quantity=info["quantity"],
                cost=info["cost"],
                case_size=info["case_size"]
            )
            item.add_vendor_info(vendor, vendor_info)

    def add_store_quantity(self, store: str, item_name: str, quantity: float) -> None:
        """
        Update or add store-specific quantity for an item.
        """
        item = self.get_or_create_item(item_name)
        item.add_store_info(store, StoreItemInfo(quantity))

    def to_dict(self) -> Dict[str, dict]:
        """
        Convert all items to a serializable dictionary format.
        """
        return {name: item.to_dict() for name, item in self.items.items()}

    def save_to_file(self, path: Union[str, Path]) -> None:
        """
        Persist all item data to a JSON file.

        Args:
            path (str or Path): Path to the JSON file.
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_from_file(self, path: Union[str, Path]) -> None:
        """
        Load item data from a JSON file into the manager.

        Args:
            path (str or Path): Path to the JSON file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item_name, item_data in data.items():
                item = Item(name=item_data["name"], item_id=item_data["id"])

                for vendor, infos in item_data.get("vendors", {}).items():
                    for info in infos:
                        item.add_vendor_info(vendor, VendorItemInfo(
                            sku=info["sku"],
                            unit=info["unit"],
                            quantity=info["quantity"],
                            cost=info["cost"],
                            case_size=info["case_size"]
                        ))

                for store, info in item_data.get("stores", {}).items():
                    item.add_store_info(store, StoreItemInfo(
                        quantity_on_hand=info["quantity_on_hand"]
                    ))

                self.items[item_name] = item
       