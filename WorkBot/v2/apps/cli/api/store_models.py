from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class StoreResult:
    id: str
    name: str
    is_active: bool

    general_manager: str | None = None
    inventory_clerk: str | None = None
    address: str | None = None
    phone_number: str | None = None
    special_notes: str = ""

    created_at: Any = None
    updated_at: Any = None

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "StoreResult":
        return cls(
            id=data["id"],
            name=data["name"],
            is_active=bool(
                data.get("is_active", True)
            ),
            general_manager=data.get(
                "general_manager"
            ),
            inventory_clerk=data.get(
                "inventory_clerk"
            ),
            address=data.get("address"),
            phone_number=data.get(
                "phone_number"
            ),
            special_notes=data.get(
                "special_notes",
                "",
            ),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )