# backend/domain/serializers/vendor_serializer.py

from pathlib import Path
from typing import Any, Dict, Optional
import json
from backend.domain.models import Store, StoreContact
from backend.app.ports.generic import Serializer
from ..formats import get_formatter 
from backend.infra.logger import Logger

@Logger.attach_logger
class StoreSerializer(Serializer[Store]):

    def __init__(self, default_format: str = 'json'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ----------------- Dumps -----------------
    def dumps(self, obj: Store, format: Optional[str] = None) -> bytes:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)
   
        if fmt in ("xlsx", "csv"):
            payload = self._to_table(self.to_dict(obj))
        else:  # json, yaml
            payload = self.to_dict(obj)
        
        return formatter.dumps(payload)

    # ----------------- Loads -----------------
    def loads(self, data: bytes, format: Optional[str] = None) -> Store:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)

        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload)
        else:  # json, yaml
            return self.from_dict(payload)

    def load_path(self, path: Path) -> Store:
        fmt = path.suffix.lstrip(".").lower()
        with open(path, "rb") as f:
            return self.loads(f.read(), fmt)

        # -------- Domain <-> dict --------
    def to_dict(self, store: Store) -> Dict[str, Any]:
        return {
            "name": store.name,
            "code": store.code,
            "special_notes": store.special_notes,
            "address": store.address,
            "phone_number": store.phone_number,
            "contacts": [
                {
                    "name": c.name,
                    "title": c.title,
                    "email": c.email,
                    "phone": c.phone,
                }
                for c in store.contacts
            ],
        }

    def from_dict(self, data: Dict[str, Any]) -> Store:
        return Store(
            name=data["name"],
            code=data.get("code", ""),
            special_notes=data.get("special_notes", ""),
            address=data.get("address", ""),
            phone_number=data.get("phone_number", ""),
            contacts=[
                StoreContact(
                    name=c.get("name", ""),
                    title=c.get("title", ""),
                    email=c.get("email", ""),
                    phone=c.get("phone", ""),
                )
                for c in data.get("contacts", [])
            ],
        )

    # -------- Domain <-> tabular --------
    def _to_table(self, data: Dict[str, Any]) -> Dict[str, Any]:

        headers = [
            "name",
            "code",
            "special_notes",
            "address",
            "phone_number",
            "contact_name",
            "contact_title",
            "contact_email",
            "contact_phone",
        ]

        rows: list[list[Any]] = []

        contacts = data.get("contacts", []) or [{}]

        for c in contacts:
            rows.append([
                data.get("name", ""),
                data.get("code", ""),
                data.get("special_notes", ""),
                data.get("address", ""),
                data.get("phone_number", ""),
                c.get("name", ""),
                c.get("title", ""),
                c.get("email", ""),
                c.get("phone", ""),
            ])

        return {"headers": headers, "rows": rows}

    def from_table(self, table: Dict[str, Any]) -> Store:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        if not rows:
            return Store(name="")

        first_row = rows[0]

        data = {
            "name": first_row[headers.index("name")],
            "code": first_row[headers.index("code")],
            "special_notes": first_row[headers.index("special_notes")],
            "address": first_row[headers.index("address")],
            "phone_number": first_row[headers.index("phone_number")],
            "contacts": [],
        }

        for row in rows:
            data["contacts"].append({
                "name": row[headers.index("contact_name")],
                "title": row[headers.index("contact_title")],
                "email": row[headers.index("contact_email")],
                "phone": row[headers.index("contact_phone")],
            })

        return self.from_dict(data)
