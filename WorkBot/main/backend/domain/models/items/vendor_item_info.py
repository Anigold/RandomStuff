from dataclasses import dataclass
from typing import Optional


@dataclass
class VendorItemInfo:

    vendor_id: str
    item_id: str
    sku: str
    order_unit: str
    
    vendor_name: str | None = None
    unit_size: Optional[float] = None

    last_price: Optional[float] = None
    last_ordered: Optional[str] = None

    is_primary: bool   = False
    is_orderable: bool = True
    is_active: bool    = True