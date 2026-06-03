from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from workbot_core.domain.models.order_line import OrderLine


class OrderStatus(StrEnum):
    PENDING    = "pending"    # Raw, downloaded order
    PROCESSED  = "processed"  # Line items have been removed or added as needed
    EXPORTED   = "exported"   # Order was exported to secondary upload file format
    FULFILLED  = "fulfilled"  # Order was placed
    CANCELLED  = "cancelled"  # Order was cancelled
    ERROR      = "error"      # Unresolvable error occurred during processing


@dataclass(frozen=True, slots=True)
class Order:
    id: str

    store_id: str
    vendor_id: str

    order_date: date
    delivery_date: date | None = None

    status: OrderStatus = OrderStatus.PENDING

    source: str | None = None
    source_reference: str | None = None

    notes: str | None = None

    lines: tuple[OrderLine, ...] = ()

    created_at: datetime | None = None
    updated_at: datetime | None = None

