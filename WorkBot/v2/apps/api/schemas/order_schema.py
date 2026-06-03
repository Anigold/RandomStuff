from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from workbot_core.domain.models.order import OrderStatus


class CreateOrderLineRequest(BaseModel):
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


class CreateOrderRequest(BaseModel):
    store_id: str
    vendor_id: str

    order_date: date
    delivery_date: date | None = None

    status: OrderStatus = OrderStatus.PENDING

    source: str | None = None
    source_reference: str | None = None

    notes: str = ""

    lines: list[CreateOrderLineRequest] = Field(default_factory=list)


class UpdateOrderNotesRequest(BaseModel):
    notes: str | None = None


class CancelOrderRequest(BaseModel):
    reason: str | None = None


class OrderLineResponse(BaseModel):
    id: str
    order_id: str

    status: str
    status_reason: str | None = None

    source_item_name: str | None = None
    source_vendor_sku: str | None = None

    quantity: Decimal
    unit: str | None = None
    unit_price_snapshot: Decimal | None = None

    item_id: str | None = None
    item_vendor_info_id: str | None = None
    item_name_snapshot: str | None = None
    vendor_sku_snapshot: str | None = None

    moved_to_order_id: str | None = None
    notes: str = ""

    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrderListResponse(BaseModel):
    id: str

    store_id: str
    store_name: str | None = None

    vendor_id: str
    vendor_name: str | None = None

    order_date: date
    delivery_date: date | None = None

    status: str
    source: str | None = None
    source_reference: str | None = None

    line_count: int

    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrderDetailResponse(OrderListResponse):
    notes: str = ""
    lines: list[OrderLineResponse]