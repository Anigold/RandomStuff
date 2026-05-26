from __future__ import annotations

from dataclasses import dataclass
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

    category:    str | None = None
    subcategory: str | None = None
    count_unit:  str | None = None
    is_active:   bool = True

    store_info:  tuple[ItemStoreInfoImportRow, ...] = ()
    vendor_info: tuple[ItemVendorInfoImportRow, ...] = ()
    