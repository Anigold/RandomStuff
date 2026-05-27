from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ItemVendorInfo:
    
    id: str

    item_id: str
    vendor_id: str

    vendor_sku: str | None = None

    purchase_unit: str | None = None

    # Number of Item.count_unit units contained in one purchase_unit.
    #
    # Examples:
    #   purchase_unit = "case", item.count_unit = "bottle", pack_size = 12
    #   purchase_unit = "bag",  item.count_unit = "lb",     pack_size = 50
    #   purchase_unit = "case", item.count_unit = "lb",     pack_size = 60
    pack_size: Decimal | None = None
    pack_size: Decimal | None = None

    price: Decimal | None = None
    last_purchase_date: date | None = None

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None