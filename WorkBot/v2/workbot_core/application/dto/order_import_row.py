from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class OrderLineImportRow:
    
    source_item_name: str

    quantity: Decimal

    source_vendor_sku: str | None = None
    unit_price: Decimal | None = None
    total_cost: Decimal | None = None

    unit: str | None = None
    notes: str = ""


@dataclass(frozen=True, slots=True)
class OrderImportRow:

    store_id: str
    vendor_id: str

    order_date: date
    delivery_date: date | None = None

    source: str | None = None
    source_reference: str | None = None

    notes: str = ""

    lines: tuple[OrderLineImportRow, ...] = field(default_factory=tuple)