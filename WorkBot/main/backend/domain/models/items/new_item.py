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
    brand: Optional[str] = None

    count_unit: Optional[str] = None
    purchase_unit: Optional[str] = None
    units_per_purchase: Optional[float] = None

    store_info: Dict[str, StoreInfo] = field(default_factory=dict)
    vendor_info: Dict[str, VendorInfo] = field(default_factory=dict)

    is_active: bool = True
    notes: Optional[str] = None