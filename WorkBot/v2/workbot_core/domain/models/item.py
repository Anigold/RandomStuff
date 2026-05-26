from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime




@dataclass(frozen=True, slots=True)
class Item:
    id: str
    name: str

    category: str | None = None
    subcategory: str | None = None

    count_unit: str | None = None

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None

    # def rename(self, name: str) -> None:
    #     cleaned = name.strip()

    #     if not cleaned:
    #         raise ValueError("Item name cannot be empty.")

    #     self.name = cleaned

    # def deactivate(self) -> None:
    #     self.is_active = False

    # def activate(self) -> None:
    #     self.is_active = True
