from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ContactInfoSchema(BaseModel):
    name: str
    title: str = ""
    email: str = ""
    phone: str = ""


class ScheduleEntrySchema(BaseModel):
    order_day: str
    delivery_days: list[str] = Field(default_factory=list)
    cutoff_time: str = ""


class OrderingInfoSchema(BaseModel):
    method: list[str] = Field(default_factory=list)
    email: str = ""
    portal_url: str = ""
    phone_number: str = ""
    schedule: list[ScheduleEntrySchema] = Field(default_factory=list)


class CreateVendorRequest(BaseModel):
    name: str

    is_active: bool = True

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: list[ContactInfoSchema] = Field(default_factory=list)
    ordering: OrderingInfoSchema = Field(default_factory=OrderingInfoSchema)

    store_ids: list[str] = Field(default_factory=list)


class UpdateVendorRequest(BaseModel):
    name: str

    is_active: bool = True

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: list[ContactInfoSchema] = Field(default_factory=list)
    ordering: OrderingInfoSchema = Field(default_factory=OrderingInfoSchema)

    store_ids: list[str] = Field(default_factory=list)


class VendorResponse(BaseModel):
    id: str
    name: str

    is_active: bool

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: list[ContactInfoSchema] = Field(default_factory=list)
    ordering: OrderingInfoSchema = Field(default_factory=OrderingInfoSchema)

    store_ids: list[str] = Field(default_factory=list)

    created_at: datetime | None = None
    updated_at: datetime | None = None