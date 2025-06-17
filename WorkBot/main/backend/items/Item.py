import uuid
import json
from typing import Dict, List, Optional, Union
from pathlib import Path


class VendorItemInfo:
    """
    Represents a vendor-specific version of an item.

    Attributes:
        sku (str): The vendor's SKU or product code.
        unit (str): The unit of measure (e.g., 'EA', 'LB').
        quantity (float): Number of units per case or package.
        cost (float): Cost per case.
        case_size (str): Original string representation of the case size (e.g., "1/12 EA").
    """

    def __init__(self, sku: str, unit: str, quantity: float, cost: float, case_size: str):
        self.sku       = sku
        self.unit      = unit
        self.quantity  = quantity
        self.cost      = cost
        self.case_size = case_size

    def to_dict(self) -> dict:
        """
        Serialize the VendorItemInfo to a dictionary for JSON persistence.
        """
        return {
            "sku": self.sku,
            "unit": self.unit,
            "quantity": self.quantity,
            "cost": self.cost,
            "case_size": self.case_size,
        }

    def __eq__(self, other) -> bool:
        return isinstance(other, VendorItemInfo) and self.sku == other.sku


class StoreItemInfo:
    """
    Represents store-specific inventory or tracking information for an item.

    Attributes:
        quantity_on_hand (float): Quantity of the item available at the store.
    """

    def __init__(self, quantity_on_hand: float = 0.0):
        self.quantity_on_hand = quantity_on_hand

    def to_dict(self) -> dict:
        """
        Serialize the StoreItemInfo to a dictionary for JSON persistence.
        """
        return {
            "quantity_on_hand": self.quantity_on_hand
        }


class Item:
    """
    Represents a unique item in the system, potentially purchased from multiple vendors
    and stocked at multiple stores.

    Attributes:
        id (str): UUID for uniquely identifying the item.
        name (str): Canonical name of the item.
        vendor_info (Dict[str, List[VendorItemInfo]]): Vendor-specific variations.
        store_info (Dict[str, StoreItemInfo]): Store-specific tracking information.
    """

    def __init__(self, name: str, item_id: Optional[str] = None):
        self.id = item_id or str(uuid.uuid4())
        self.name = name
        self.vendor_info: Dict[str, List[VendorItemInfo]] = {}
        self.store_info: Dict[str, StoreItemInfo] = {}

    def add_vendor_info(self, vendor: str, info: VendorItemInfo) -> None:
        """
        Add or update vendor-specific variant of this item.
        Avoids duplication based on SKU.
        """
        if vendor not in self.vendor_info:
            self.vendor_info[vendor] = []

        if info not in self.vendor_info[vendor]:
            self.vendor_info[vendor].append(info)

    def add_store_info(self, store: str, info: StoreItemInfo) -> None:
        """
        Add or update store-specific information for this item.
        """
        self.store_info[store] = info

    def to_dict(self) -> dict:
        """
        Serialize the Item to a dictionary for JSON persistence.
        """
        return {
            "id": self.id,
            "name": self.name,
            "vendors": {
                v: [i.to_dict() for i in infos]
                for v, infos in self.vendor_info.items()
            },
            "stores": {
                s: info.to_dict()
                for s, info in self.store_info.items()
            }
        }


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
