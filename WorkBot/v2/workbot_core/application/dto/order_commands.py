from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from workbot_core.domain.models.order import OrderStatus


@dataclass(frozen=True, slots=True)
class CreateOrderLineCommand:
    source_item_name: str | None = None
    source_vendor_sku: str | None = None

    item_id: str | None = None
    item_vendor_info_id: str | None = None

    item_name_snapshot: str | None = None
    vendor_sku_snapshot: str | None = None
    unit_price_snapshot: Decimal | None = None

    quantity: Decimal = Decimal("0")
    unit: str | None = None

    notes: str = ""


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    store_id: str
    vendor_id: str

    order_date: date
    delivery_date: date | None = None

    status: OrderStatus = OrderStatus.PENDING

    source: str | None = None
    source_reference: str | None = None

    notes: str = ""

    lines: tuple[CreateOrderLineCommand, ...] = ()


@dataclass(frozen=True, slots=True)
class UpdateOrderNotesCommand:
    order_id: str
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CancelOrderCommand:
    order_id: str
    reason: str | None = None