from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ContactInfo:
    name:  str
    title: str = ""
    email: str = ""
    phone: str = ""


@dataclass(frozen=True, slots=True)
class ScheduleEntry:
    order_day:     str
    delivery_days: tuple[str, ...] = ()
    cutoff_time:   str = ""


@dataclass(frozen=True, slots=True)
class OrderingInfo:
    method:       tuple[str, ...] = ()
    email:        str = ""
    portal_url:   str = ""
    phone_number: str = ""
    schedule:     tuple[ScheduleEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class Vendor:
    id: str
    name: str

    is_active: bool = True

    order_format: str = ""
    special_notes: str = ""

    min_order_value: Decimal = Decimal("0")
    min_order_cases: int = 0

    internal_contacts: tuple[ContactInfo, ...] = ()
    ordering: OrderingInfo = OrderingInfo()

    store_ids: tuple[str, ...] = ()