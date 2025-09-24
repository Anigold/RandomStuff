# backend/domain/serializers/vendor_serializer.py

from pathlib import Path
from typing import Any, Dict, Optional
import json
from backend.domain.models.vendor import Vendor, ContactInfo, OrderingInfo, ScheduleEntry
from backend.app.ports.generic import Serializer
from ..formats import get_formatter  # registry, like in OrderSerializer
from backend.infra.logger import Logger

@Logger.attach_logger
class VendorSerializer(Serializer[Vendor]):
    """
    Domain serializer for Vendor.
    - Knows how to convert Vendor ↔ dict (nested) ↔ tabular {headers, rows}.
    - Delegates bytes conversion to formatters.
    """

    def __init__(self, default_format: str = "json"):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ----------------- Dumps -----------------
    def dumps(self, obj: Vendor, format: Optional[str] = None) -> bytes:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)
   
        if fmt in ("xlsx", "csv"):
            payload = self._to_table(self.to_dict(obj))
        else:  # json, yaml
            payload = self.to_dict(obj)
        
        return formatter.dumps(payload)

    # ----------------- Loads -----------------
    def loads(self, data: bytes, format: Optional[str] = None) -> Vendor:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)

        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload)
        else:  # json, yaml
            return self.from_dict(payload)

    def load_path(self, path: Path) -> Vendor:
        fmt = path.suffix.lstrip(".").lower()
        with open(path, "rb") as f:
            return self.loads(f.read(), fmt)

    # ----------------- Domain <-> dict -----------------
    def to_dict(self, vendor: Vendor) -> dict:
        return {
            "name": vendor.name,
            "order_format": vendor.order_format,
            "special_notes": vendor.special_notes,
            "min_order_value": vendor.min_order_value,
            "min_order_cases": vendor.min_order_cases,
            "internal_contacts": [
                {
                    "name": c.name,
                    "title": c.title,
                    "email": c.email,
                    "phone": c.phone,
                }
                for c in vendor.internal_contacts
            ],
            "ordering": {
                "method": vendor.ordering.method,
                "email": vendor.ordering.email,
                "portal_url": vendor.ordering.portal_url,
                "phone_number": vendor.ordering.phone_number,
                "schedule": [
                    {
                        "order_day": s.order_day,
                        "delivery_days": s.delivery_days,
                        "cutoff_time": s.cutoff_time,
                    }
                    for s in vendor.ordering.schedule
                ],
            },
            "store_ids": vendor.store_ids,
        }

    def from_dict(self, data: dict) -> Vendor:
        return Vendor(
            name=data["name"],
            order_format=data.get("order_format", ""),
            special_notes=data.get("special_notes", ""),
            min_order_value=data.get("min_order_value", 0),
            min_order_cases=data.get("min_order_cases", 0),
            internal_contacts=[
                ContactInfo(
                    name=c.get("name", ""),
                    title=c.get("title", ""),
                    email=c.get("email", ""),
                    phone=c.get("phone", ""),
                )
                for c in data.get("internal_contacts", [])
            ],
            ordering=OrderingInfo(
                method=data.get("ordering", {}).get("method", []),
                email=data.get("ordering", {}).get("email", ""),
                portal_url=data.get("ordering", {}).get("portal_url", ""),
                phone_number=data.get("ordering", {}).get("phone_number", ""),
                schedule=[
                    ScheduleEntry(
                        order_day=s.get("order_day", ""),
                        delivery_days=s.get("delivery_days", []),
                        cutoff_time=s.get("cutoff_time", ""),
                    )
                    for s in data.get("ordering", {}).get("schedule", [])
                ],
            ),
            store_ids=data.get("store_ids", {}),
        )

    # ----------------- Domain <-> table -----------------
    def _to_table(self, data: dict) -> dict[str, Any]:
        headers = [
            "name",
            "order_format",
            "special_notes",
            "min_order_value",
            "min_order_cases",
            "contact_name",
            "contact_title",
            "contact_email",
            "contact_phone",
            "order_methods",
            "ordering_email",
            "portal_url",
            "ordering_phone",
            "order_day",
            "delivery_days",
            "cutoff_time",
            "store_ids",
        ]

        rows: list[list[Any]] = []

        contacts = data.get("internal_contacts", []) or [{}]
        schedules = data.get("ordering", {}).get("schedule", []) or [{}]

        for c in contacts:
            for s in schedules:
                rows.append([
                    data.get("name", ""),
                    data.get("order_format", ""),
                    data.get("special_notes", ""),
                    data.get("min_order_value", 0),
                    data.get("min_order_cases", 0),
                    c.get("name", ""),
                    c.get("title", ""),
                    c.get("email", ""),
                    c.get("phone", ""),
                    ", ".join(data.get("ordering", {}).get("method", [])),
                    data.get("ordering", {}).get("email", ""),
                    data.get("ordering", {}).get("portal_url", ""),
                    data.get("ordering", {}).get("phone_number", ""),
                    s.get("order_day", ""),
                    ", ".join(s.get("delivery_days", [])),
                    s.get("cutoff_time", ""),
                    json.dumps(data.get("store_ids", {})),
                ])

        return {"headers": headers, "rows": rows}

    def from_table(self, table: dict) -> Vendor:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        if not rows:
            return Vendor(name="")

        first_row = rows[0]

        data = {
            "name": first_row[headers.index("name")],
            "order_format": first_row[headers.index("order_format")],
            "special_notes": first_row[headers.index("special_notes")],
            "min_order_value": first_row[headers.index("min_order_value")],
            "min_order_cases": first_row[headers.index("min_order_cases")],
            "internal_contacts": [],
            "ordering": {
                "method": first_row[headers.index("order_methods")].split(", "),
                "email": first_row[headers.index("ordering_email")],
                "portal_url": first_row[headers.index("portal_url")],
                "phone_number": first_row[headers.index("ordering_phone")],
                "schedule": [],
            },
            "store_ids": json.loads(first_row[headers.index("store_ids")]),
        }

        for row in rows:
            data["internal_contacts"].append({
                "name": row[headers.index("contact_name")],
                "title": row[headers.index("contact_title")],
                "email": row[headers.index("contact_email")],
                "phone": row[headers.index("contact_phone")],
            })
            data["ordering"]["schedule"].append({
                "order_day": row[headers.index("order_day")],
                "delivery_days": row[headers.index("delivery_days")].split(", "),
                "cutoff_time": row[headers.index("cutoff_time")],
            })

        return self.from_dict(data)
