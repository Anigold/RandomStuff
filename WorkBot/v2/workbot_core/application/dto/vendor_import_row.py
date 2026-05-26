from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ContactInfoImportRow:
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""


@dataclass(frozen=True, slots=True)
class ScheduleEntryImportRow:
    order_day: str = ""
    delivery_days: tuple[str, ...] = ()
    cutoff_time: str = ""


@dataclass(frozen=True, slots=True)
class OrderingInfoImportRow:
    method: tuple[str, ...] = ()
    email: str = ""
    portal_url: str = ""
    phone_number: str = ""
    schedule: tuple[ScheduleEntryImportRow, ...] = ()


@dataclass(frozen=True, slots=True)
class VendorImportRow:
    id: str | None
    name: str

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: tuple[ContactInfoImportRow, ...] = ()
    ordering: OrderingInfoImportRow = field(default_factory=OrderingInfoImportRow)

    store_names: tuple[str, ...] = ()