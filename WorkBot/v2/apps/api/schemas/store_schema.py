# apps/api/schemas/store_schema.py

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CreateStoreRequest(BaseModel):
    name: str

    is_active: bool = True

    general_manager: str | None = None
    inventory_clerk: str | None = None

    address: str | None = None
    phone_number: str | None = None
    special_notes: str | None = None


class UpdateStoreRequest(BaseModel):
    name: str

    is_active: bool = True

    general_manager: str | None = None
    inventory_clerk: str | None = None

    address: str | None = None
    phone_number: str | None = None
    special_notes: str | None = None


class StoreResponse(BaseModel):
    id: str
    name: str

    is_active: bool

    general_manager: str | None = None
    inventory_clerk: str | None = None

    address: str | None = None
    phone_number: str | None = None
    special_notes: str = ""

    created_at: datetime | None = None
    updated_at: datetime | None = None