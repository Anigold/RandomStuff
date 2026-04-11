from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class StoreInfo:
    store: str
    par: Optional[float] = None
    on_hand: Optional[float] = None
    

@dataclass
class VendorInfo:
    vendor: str

    sku: str
    order_unit: str
    unit_size: Optional[float] = None

    price: Optional[float] = None

    is_primary: bool = False


@dataclass
class Item:
    id: str
    name: str

    category: Optional[str] = None
    subcategory: Optional[str] = None

    count_unit: Optional[str] = None

    store_info: Dict[str, StoreInfo] = field(default_factory=dict)
    vendor_info: Dict[str, VendorInfo] = field(default_factory=dict)

    is_active: bool = True
    is_inventoried: bool = True

    notes: Optional[str] = None

    aliases: list[str] = field(default_factory=list)