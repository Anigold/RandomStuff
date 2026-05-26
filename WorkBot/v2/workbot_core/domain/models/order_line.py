from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class OrderLineStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    MOVED = "moved"
    REMOVED = "removed"
    IGNORED = "ignored"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class OrderLine:
    id: str
    order_id: str

    item_id: str | None = None
    item_vendor_info_id: str | None = None

    source_item_name: str | None = None
    source_vendor_sku: str | None = None

    item_name_snapshot: str | None = None
    vendor_sku_snapshot: str | None = None
    unit_price_snapshot: Decimal | None = None

    quantity: Decimal = Decimal("0")
    unit: str | None = None

    status: OrderLineStatus = OrderLineStatus.PENDING
    status_reason: str | None = None

    moved_to_order_id: str | None = None

    notes: str = ""

    created_at: datetime | None = None
    updated_at: datetime | None = None