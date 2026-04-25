from dataclasses import dataclass, field
from typing import Dict, Optional

from .store_item_info import StoreItemInfo
from .vendor_item_info import VendorItemInfo


@dataclass
class Item:
    id: str
    name: str

    category: Optional[str] = None
    subcategory: Optional[str] = None

    count_unit: Optional[str] = None

    store_info: Dict[str, StoreItemInfo] = field(default_factory=dict)
    vendor_info: Dict[str, VendorItemInfo] = field(default_factory=dict)

    is_active: bool = True
    is_inventoried: bool = True

    notes: Optional[str] = None

    aliases: list[str] = field(default_factory=list)