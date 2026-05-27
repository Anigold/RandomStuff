from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Item:
    id: str
    name: str

    category: str | None = None
    subcategory: str | None = None

    # Business counting unit.
    #
    # Examples:
    #   1 steak
    #   1 bottle
    #   1 lb
    #   1 bag
    #
    # ItemVendorInfo.pack_size should mean:
    #   number of these count units per vendor purchase unit.
    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None

    # Optional display/source label for the counted unit.
    custom_each_name: str | None = None

    # Optional descriptive "each" metadata for one count unit.
    each_quantity: Decimal | None = None
    each_measure: str | None = None

    # Optional descriptive weight of one count unit.
    weight_quantity: Decimal | None = None
    weight_measure: str | None = None

    # Optional descriptive volume of one count unit.
    volume_quantity: Decimal | None = None
    volume_measure: str | None = None

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None