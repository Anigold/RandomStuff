from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CreateItemCommand:
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


@dataclass(frozen=True, slots=True)
class AddItemVendorInfoCommand:
    item_id: str
    vendor_id: str

    vendor_sku: str | None = None
    purchase_unit: str | None = None
    pack_size: Decimal | None = None
    price: Decimal | None = None

    is_active: bool = True


@dataclass(frozen=True, slots=True)
class AddItemStoreInfoCommand:
    item_id: str
    store_id: str

    count_unit: str | None = None
    par: Decimal | None = None

    is_active: bool = True