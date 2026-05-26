from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from workbot_core.application.dto.vendor_import_row import (
    ContactInfoImportRow,
    OrderingInfoImportRow,
    ScheduleEntryImportRow,
    VendorImportRow,
)


class LegacyVendorReader:
    """Reads legacy vendor JSON files and converts them into VendorImportRow DTOs."""

    def read_directory(self, directory: Path) -> list[VendorImportRow]:
        if not directory.exists():
            raise FileNotFoundError(f"Vendor directory does not exist: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"Expected vendor directory, got: {directory}")

        rows: list[VendorImportRow] = []

        for path in sorted(directory.glob("*.json")):
            rows.append(self.read_file(path))

        return rows

    def read_file(self, path: Path) -> VendorImportRow:
        if not path.exists():
            raise FileNotFoundError(f"Vendor file does not exist: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in vendor file: {path}")

        return self._row_from_dict(data)

    def _row_from_dict(self, data: dict[str, Any]) -> VendorImportRow:
        return VendorImportRow(
            id=self._optional_str(data.get("id")),
            name=self._required_str(data.get("name"), "name"),
            order_format=self._text(data.get("order_format")),
            special_notes=self._text(data.get("special_notes")),
            min_order_value=self._decimal(data.get("min_order_value")),
            min_order_cases=self._int(data.get("min_order_cases")),
            internal_contacts=self._contacts(data.get("internal_contacts")),
            ordering=self._ordering(data.get("ordering")),
            store_names=self._store_names(data.get("store_ids")),
        )

    def _contacts(self, raw: object) -> tuple[ContactInfoImportRow, ...]:
        if raw is None:
            return ()

        if not isinstance(raw, list):
            raise ValueError("internal_contacts must be a list.")

        contacts: list[ContactInfoImportRow] = []

        for item in raw:
            if not isinstance(item, dict):
                continue

            contacts.append(
                ContactInfoImportRow(
                    name=self._text(item.get("name")),
                    title=self._text(item.get("title")),
                    email=self._text(item.get("email")),
                    phone=self._text(item.get("phone")),
                )
            )

        return tuple(contacts)

    def _ordering(self, raw: object) -> OrderingInfoImportRow:
        if raw is None:
            return OrderingInfoImportRow()

        if not isinstance(raw, dict):
            raise ValueError("ordering must be an object/dict.")

        return OrderingInfoImportRow(
            method=self._string_tuple(raw.get("method")),
            email=self._text(raw.get("email")),
            portal_url=self._text(raw.get("portal_url")),
            phone_number=self._text(raw.get("phone_number")),
            schedule=self._schedule(raw.get("schedule")),
        )

    def _schedule(self, raw: object) -> tuple[ScheduleEntryImportRow, ...]:
        if raw is None:
            return ()

        if not isinstance(raw, list):
            raise ValueError("ordering.schedule must be a list.")

        entries: list[ScheduleEntryImportRow] = []

        for item in raw:
            if not isinstance(item, dict):
                continue

            entries.append(
                ScheduleEntryImportRow(
                    order_day=self._text(item.get("order_day")),
                    delivery_days=self._string_tuple(item.get("delivery_days")),
                    cutoff_time=self._text(item.get("cutoff_time")),
                )
            )

        return tuple(entries)

    def _store_names(self, raw: object) -> tuple[str, ...]:
        if raw is None:
            return ()

        if not isinstance(raw, dict):
            raise ValueError("store_ids must be an object/dict.")

        # Legacy shape is {"Bakery": "", "Triphammer": ""}.
        # Keys are the store names.
        return tuple(
            name
            for name in (self._text(key) for key in raw.keys())
            if name
        )

    @staticmethod
    def _text(value: object) -> str:
        if value is None:
            return ""

        return str(value).strip()

    @classmethod
    def _required_str(cls, value: object, field_name: str) -> str:
        cleaned = cls._text(value)

        if not cleaned:
            raise ValueError(f"Missing required field: {field_name}")

        return cleaned

    @classmethod
    def _optional_str(cls, value: object) -> str | None:
        cleaned = cls._text(value)

        return cleaned or None

    @classmethod
    def _string_tuple(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()

        if isinstance(value, str):
            cleaned = cls._text(value)
            return (cleaned,) if cleaned else ()

        if not isinstance(value, list):
            return ()

        return tuple(
            cleaned
            for cleaned in (cls._text(item) for item in value)
            if cleaned
        )

    @staticmethod
    def _decimal(value: object) -> Decimal:
        if value is None or value == "":
            return Decimal("0")

        try:
            return Decimal(str(value).strip())
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal value: {value!r}") from exc

    @staticmethod
    def _int(value: object) -> int:
        if value is None or value == "":
            return 0

        return int(value)