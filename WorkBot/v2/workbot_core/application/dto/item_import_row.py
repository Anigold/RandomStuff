from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ItemVendorInfoImportRow:
    vendor_id:     str
    vendor_sku:    str | None = None
    purchase_unit: str | None = None
    pack_size:     Decimal | None = None
    price:         Decimal | None = None


@dataclass(frozen=True, slots=True)
class ItemStoreInfoImportRow:
    store_id:        str
    count_unit:      str | None = None
    par:             Decimal | None = None


@dataclass(frozen=True, slots=True)
class ItemImportRow:
    id: str
    name: str

    category: str | None = None
    subcategory: str | None = None

    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None

    custom_each_name: str | None = None

    each_quantity: Decimal | None = None
    each_measure: str | None = None

    weight_quantity: Decimal | None = None
    weight_measure: str | None = None

    volume_quantity: Decimal | None = None
    volume_measure: str | None = None

    is_active: bool = True

    vendor_info: tuple[ItemVendorInfoImportRow, ...] = field(default_factory=tuple)
    store_info: tuple[ItemStoreInfoImportRow, ...] = field(default_factory=tuple)