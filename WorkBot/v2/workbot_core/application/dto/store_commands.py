from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateStoreCommand:
    name: str

    is_active: bool = True

    general_manager: str | None = None
    inventory_clerk: str | None = None

    address: str | None = None
    phone_number: str | None = None
    special_notes: str = ""


@dataclass(frozen=True, slots=True)
class UpdateStoreCommand:
    store_id: str
    name: str

    is_active: bool = True

    general_manager: str | None = None
    inventory_clerk: str | None = None

    address: str | None = None
    phone_number: str | None = None
    special_notes: str = ""