from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from workbot_core.application.dto.item_import_row import (
    ItemImportRow,
    ItemStoreInfoImportRow,
    ItemVendorInfoImportRow,
)


class LegacyItemReader:
    """Reads legacy item JSON files and converts them into ItemImportRow DTOs.

    This reader does not save anything to the database. It only translates
    legacy file data into import DTOs for the ImportItems use case.
    """

    def read_directory(self, directory: Path) -> list[ItemImportRow]:
        if not directory.exists():
            raise FileNotFoundError(f"Item directory does not exist: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"Expected item directory, got: {directory}")

        rows: list[ItemImportRow] = []

        for path in sorted(directory.glob("*.json")):
            rows.append(self.read_file(path))

        return rows

    def read_file(self, path: Path) -> ItemImportRow:
        if not path.exists():
            raise FileNotFoundError(f"Item file does not exist: {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object in item file: {path}")

        return self._row_from_dict(data)

    def _row_from_dict(self, data: dict[str, Any]) -> ItemImportRow:
        return ItemImportRow(
            id=self._required_str(data.get("id"), "id"),
            name=self._required_str(data.get("name"), "name"),
            category=self._optional_str(data.get("category")),
            subcategory=self._optional_str(data.get("subcategory")),
            count_unit=self._optional_str(data.get("count_unit")),
            is_active=self._optional_bool(data.get("is_active"), default=True),
            vendor_info=self._vendor_info_rows(data.get("vendor_info")),
            store_info=self._store_info_rows(data.get("store_info")),
        )

    def _vendor_info_rows(self, raw: object) -> tuple[ItemVendorInfoImportRow, ...]:
        if raw is None:
            return ()

        if not isinstance(raw, dict):
            raise ValueError("vendor_info must be an object/dict.")

        rows: list[ItemVendorInfoImportRow] = []

        for vendor_id, info in raw.items():
            if not isinstance(info, dict):
                continue

            rows.append(
                ItemVendorInfoImportRow(
                    vendor_id=self._required_str(vendor_id, "vendor_id"),
                    vendor_sku=self._optional_str(
                        info.get("vendor_sku")
                        or info.get("sku")
                        or info.get("item_number")
                    ),
                    purchase_unit=self._optional_str(
                        info.get("purchase_unit")
                        or info.get("unit")
                        or info.get("order_unit")
                    ),
                    pack_size=self._optional_decimal(
                        info.get("pack_size")
                        or info.get("case_size")
                        or info.get("pack")
                    ),
                    price=self._optional_decimal(
                        info.get("price")
                        or info.get("unit_price")
                        or info.get("last_price")
                    ),
                )
            )

        return tuple(rows)

    def _store_info_rows(self, raw: object) -> tuple[ItemStoreInfoImportRow, ...]:
        if raw is None:
            return ()

        if not isinstance(raw, dict):
            raise ValueError("store_info must be an object/dict.")

        rows: list[ItemStoreInfoImportRow] = []

        for store_id, info in raw.items():
            if not isinstance(info, dict):
                continue

            rows.append(
                ItemStoreInfoImportRow(
                    store_id=self._required_str(store_id, "store_id"),
                    count_unit=self._optional_str(
                        info.get("count_unit")
                        or info.get("unit")
                    ),
                    par=self._optional_decimal(info.get("par")),
                )
            )

        return tuple(rows)

    @staticmethod
    def _required_str(value: object, field_name: str) -> str:
        if value is None:
            raise ValueError(f"Missing required field: {field_name}")

        cleaned = str(value).strip()

        if not cleaned:
            raise ValueError(f"Required field cannot be empty: {field_name}")

        return cleaned

    @staticmethod
    def _optional_str(value: object) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    @staticmethod
    def _optional_bool(value: object, *, default: bool) -> bool:
        if value is None:
            return default

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {"true", "1", "yes", "y"}:
                return True

            if normalized in {"false", "0", "no", "n"}:
                return False

        return bool(value)

    @staticmethod
    def _optional_decimal(value: object) -> Decimal | None:
        if value is None or value == "":
            return None

        try:
            return Decimal(str(value).strip())
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal value: {value!r}") from exc