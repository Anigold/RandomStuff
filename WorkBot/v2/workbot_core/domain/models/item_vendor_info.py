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
    pack_size: Decimal | None = None

    price: Decimal | None = None
    last_purchase_date: date | None = None

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None