from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum


class InventoryCountStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


@dataclass(frozen=True, slots=True)
class InventoryCountLine:
    id: str
    inventory_count_id: str
    item_id: str
    quantity: Decimal
    unit: str
    notes: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class InventoryCount:
    id: str
    store_id: str
    count_date: date
    status: InventoryCountStatus = InventoryCountStatus.DRAFT
    notes: str | None = None
    lines: tuple[InventoryCountLine, ...] = field(default_factory=tuple)

    created_at: datetime | None = None
    updated_at: datetime | None = None

    def submit(self) -> InventoryCount:
        if self.status == InventoryCountStatus.SUBMITTED:
            return self

        return replace(
            self,
            status=InventoryCountStatus.SUBMITTED,
        )