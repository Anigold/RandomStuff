from dataclasses import dataclass
from typing import Optional


@dataclass
class VendorItemInfo:
    vendor: str

    sku: str
    order_unit: str
    unit_size: Optional[float] = None

    price: Optional[float] = None

    is_primary: bool = False