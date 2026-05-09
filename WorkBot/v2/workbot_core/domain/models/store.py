from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Store:
    id: str
    name: str
    is_active: bool = True

    general_manager = None
    inventory_clerk = None

    address: str = None
    phone_number: str = None
    special_notes: str = ''