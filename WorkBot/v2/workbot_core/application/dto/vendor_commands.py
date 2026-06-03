from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from workbot_core.domain.models.vendor import ContactInfo, OrderingInfo, VendorStoreReference


@dataclass(frozen=True, slots=True)
class CreateVendorCommand:
    name: str

    is_active: bool = True

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: tuple[ContactInfo, ...] = ()
    ordering: OrderingInfo = OrderingInfo()

    store_references: tuple[VendorStoreReference, ...] = ()


@dataclass(frozen=True, slots=True)
class UpdateVendorCommand:
    vendor_id: str
    name: str

    is_active: bool = True

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: tuple[ContactInfo, ...] = ()
    ordering: OrderingInfo = OrderingInfo()

    store_references: tuple[VendorStoreReference, ...] = ()