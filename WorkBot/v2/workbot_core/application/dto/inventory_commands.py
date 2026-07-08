from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CreateInventoryCountLineCommand:
    item_id: str
    quantity: Decimal
    unit: str
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class CreateInventoryCountCommand:
    store_id: str
    count_date: date
    notes: str | None
    lines: tuple[CreateInventoryCountLineCommand, ...]