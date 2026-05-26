from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ItemStoreInfo:

    id: str

    item_id: str
    store_id: str

    count_unit: str | None = None
    par: Decimal | None = None

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None