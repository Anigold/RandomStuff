from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class InventoryItemResponse(BaseModel):
    id: str
    name: str
    category: str | None = None
    subcategory: str | None = None
    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None
    is_active: bool


class InventoryCountLineRequest(BaseModel):
    item_id: str
    quantity: Decimal
    unit: str
    notes: str | None = None


class CreateInventoryCountRequest(BaseModel):
    count_date: date
    notes: str | None = None
    lines: list[InventoryCountLineRequest]


class InventoryCountLineResponse(BaseModel):
    id: str
    inventory_count_id: str
    item_id: str
    item_name: str | None = None
    quantity: Decimal
    unit: str
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InventoryCountResponse(BaseModel):
    id: str
    store_id: str
    count_date: date
    status: str
    notes: str | None = None
    lines: list[InventoryCountLineResponse]
    created_at: datetime | None = None
    updated_at: datetime | None = None