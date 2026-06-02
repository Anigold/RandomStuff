from __future__ import annotations

from decimal import Decimal
from typing import Any

from workbot_core.domain.models.vendor import (
    ContactInfo,
    OrderingInfo,
    ScheduleEntry,
    Vendor,
)
from workbot_core.infrastructure.database.records.vendor_record import VendorRecord


def vendor_record_to_domain(record: VendorRecord) -> Vendor:
    return Vendor(
        id=record.id,
        name=record.name,
        is_active=record.is_active,
        order_format=record.order_format or "",
        special_notes=record.special_notes or "",
        min_order_value=record.min_order_value or Decimal("0"),
        min_order_cases=record.min_order_cases or 0,
        internal_contacts=_contacts_from_json(record.internal_contacts_json),
        ordering=_ordering_from_json(record.ordering_json),
        store_ids=tuple(record.store_ids_json or ()),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def vendor_to_record(vendor: Vendor) -> VendorRecord:
    return VendorRecord(
        id=vendor.id,
        name=vendor.name,
        is_active=vendor.is_active,
        order_format=vendor.order_format,
        special_notes=vendor.special_notes,
        min_order_value=vendor.min_order_value,
        min_order_cases=vendor.min_order_cases,
        internal_contacts_json=_contacts_to_json(vendor.internal_contacts),
        ordering_json=_ordering_to_json(vendor.ordering),
        store_ids_json=list(vendor.store_ids),
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
    )


def update_vendor_record(record: VendorRecord, vendor: Vendor) -> None:
    record.name = vendor.name
    record.is_active = vendor.is_active
    record.order_format = vendor.order_format
    record.special_notes = vendor.special_notes
    record.min_order_value = vendor.min_order_value
    record.min_order_cases = vendor.min_order_cases
    record.internal_contacts_json = _contacts_to_json(vendor.internal_contacts)
    record.ordering_json = _ordering_to_json(vendor.ordering)
    record.store_ids_json = list(vendor.store_ids)
    record.created_at = vendor.created_at
    record.updated_at = vendor.updated_at


def _contacts_to_json(contacts: tuple[ContactInfo, ...]) -> list[dict[str, str]]:
    return [
        {
            "name": contact.name,
            "title": contact.title,
            "email": contact.email,
            "phone": contact.phone,
        }
        for contact in contacts
    ]


def _contacts_from_json(raw: Any) -> tuple[ContactInfo, ...]:
    if not raw:
        return ()

    return tuple(
        ContactInfo(
            name=str(item.get("name", "")),
            title=str(item.get("title", "")),
            email=str(item.get("email", "")),
            phone=str(item.get("phone", "")),
        )
        for item in raw
        if isinstance(item, dict)
    )


def _ordering_to_json(ordering: OrderingInfo) -> dict[str, Any]:
    return {
        "method": list(ordering.method),
        "email": ordering.email,
        "portal_url": ordering.portal_url,
        "phone_number": ordering.phone_number,
        "schedule": [
            {
                "order_day": entry.order_day,
                "delivery_days": list(entry.delivery_days),
                "cutoff_time": entry.cutoff_time,
            }
            for entry in ordering.schedule
        ],
    }


def _ordering_from_json(raw: Any) -> OrderingInfo:
    if not isinstance(raw, dict):
        return OrderingInfo()

    return OrderingInfo(
        method=tuple(raw.get("method") or ()),
        email=str(raw.get("email", "")),
        portal_url=str(raw.get("portal_url", "")),
        phone_number=str(raw.get("phone_number", "")),
        schedule=_schedule_from_json(raw.get("schedule")),
    )


def _schedule_from_json(raw: Any) -> tuple[ScheduleEntry, ...]:
    if not raw:
        return ()

    return tuple(
        ScheduleEntry(
            order_day=str(item.get("order_day", "")),
            delivery_days=tuple(item.get("delivery_days") or ()),
            cutoff_time=str(item.get("cutoff_time", "")),
        )
        for item in raw
        if isinstance(item, dict)
    )