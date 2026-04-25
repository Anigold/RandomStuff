from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from backend.domain.models import Item, VendorItemInfo, StoreItemInfo
from backend.core.interfaces.serializer import Serializer
from backend.core.interfaces.formatter import BaseFormatter
from backend.infra.logger import Logger

from ..formats import get_formatter


@Logger.attach_logger
class ItemSerializer(Serializer[Item]):
    """
    Domain serializer: maps Item <-> dict / tabular payloads.

    Format behavior:
    - json: nested object structure
    - xlsx: multi-table workbook structure
    - csv: single selected table
    """

    def __init__(self, default_format: str = "json"):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ------------------------------------------------------------------
    # Core protocol
    # ------------------------------------------------------------------

    def dumps(
        self,
        obj: Item,
        format: Optional[str] = None,
        context: dict | None = None,
    ) -> bytes:
        fmt = (format or self.preferred_format()).lower()
        formatter = self.get_formatter(fmt)
        context = context or {}

        if fmt == "json":
            payload = self.to_dict(obj)

        elif fmt == "xlsx":
            payload = self.to_workbook(obj, context=context)

        elif fmt == "csv":
            table_name = context.get("table", "item")
            workbook = self.to_workbook(obj, context=context)
            if table_name not in workbook:
                raise ValueError(
                    f"Unknown table '{table_name}'. "
                    f"Available tables: {list(workbook.keys())}"
                )
            payload = workbook[table_name]

        else:
            raise ValueError(f"Unsupported format for ItemSerializer: {fmt}")

        return formatter.dumps(payload, context=context)

    def loads(self, data: bytes, format: Optional[str] = None) -> Item:
        fmt = (format or self.preferred_format()).lower()
        formatter = self.get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt == "json":
            return self.from_dict(payload)

        if fmt == "xlsx":
            return self.from_workbook(payload)

        if fmt == "csv":
            return self.from_table(payload)

        raise ValueError(f"Unsupported format for ItemSerializer: {fmt}")

    def load_path(self, path: Path, context: dict | None = None) -> Item:
        fmt = path.suffix.lstrip(".").lower()
        formatter = self.get_formatter(fmt)
        payload = formatter.load_path(
            path, 
            # context=context
            )
        
        if fmt == "json":
            return self.from_dict(payload)

        if fmt == "xlsx":
            return self.from_workbook(payload)

        if fmt == "csv":
            return self.from_table(payload)

        raise ValueError(f"Unsupported format for ItemSerializer: {fmt}")

    def get_formatter(self, fmt: str) -> BaseFormatter:
        return get_formatter(fmt)

    # ------------------------------------------------------------------
    # Domain <-> dict
    # ------------------------------------------------------------------

    def to_dict(self, item: Item) -> dict[str, Any]:
        return {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "subcategory": item.subcategory,
            "count_unit": item.count_unit,
            "vendor_info": [
                {
                    "vendor": v.vendor,
                    "sku": v.sku,
                    "unit": v.unit,
                    "quantity": v.quantity,
                    "cost": v.cost,
                }
                for v in item.vendor_info
            ],
            "store_info": [
                {
                    "store": getattr(s, "store", None),
                    "quantity_on_hand": s.quantity_on_hand,
                }
                for s in item.store_info
            ],
            "is_active": item.is_active,
            "is_inventoried": item.is_inventoried,
            "notes": item.notes,
            "aliases": item.aliases,
        }

    def from_dict(self, data: dict[str, Any]) -> Item:
        vendor_info_data = data.get("vendor_info") or []
        store_info_data = data.get("store_info") or []

        return Item(
            id=data["id"],
            name=data["name"],
            category=data.get("category"),
            subcategory=data.get("subcategory"),
            count_unit=data.get("count_unit"),
            vendor_info=[
                VendorItemInfo(
                    vendor=v["vendor"],
                    sku=v.get("sku"),
                    unit=v.get("unit"),
                    quantity=v.get("quantity"),
                    cost=v.get("cost"),
                )
                for v in vendor_info_data
            ],
            store_info=[
                self._build_store_info_from_dict(s)
                for s in store_info_data
            ],
            is_active=data.get("is_active", True),
            is_inventoried=data.get("is_inventoried", True),
            notes=data.get("notes"),
            aliases=data.get("aliases") or [],
        )
    # ------------------------------------------------------------------
    # Domain <-> workbook / tables
    # ------------------------------------------------------------------

    def to_workbook(
        self,
        item: Item,
        context: dict | None = None,
    ) -> dict[str, dict[str, Any]]:
        return {
            "item": self._item_table(item),
            "vendor_info": self._vendor_table(item),
            "store_info": self._store_table(item),
        }

    def from_workbook(self, payload: dict[str, Any]) -> Item:
        """
        Accepts either:
        - a workbook payload: {"item": {...}, "vendor_info": {...}, "store_info": {...}}
        - a single table payload: {"headers": [...], "rows": [...]}
        """
        if self._is_single_table(payload):
            return self.from_table(payload)

        item_table = payload.get("item", {"headers": [], "rows": [], "metadata": {}})
        vendor_table = payload.get(
            "vendor_info", {"headers": [], "rows": [], "metadata": {}}
        )
        store_table = payload.get(
            "store_info", {"headers": [], "rows": [], "metadata": {}}
        )

        item_rows = item_table.get("rows", [])
        if not item_rows:
            raise ValueError("Workbook payload missing required 'item' row.")

        item_headers = item_table.get("headers", [])
        item_row_dict = self._row_to_dict(item_headers, item_rows[0])

        vendor_rows = vendor_table.get("rows", [])
        vendor_headers = vendor_table.get("headers", [])
        vendor_info = [
            VendorItemInfo(
                vendor=row_dict.get("Vendor"),
                sku=row_dict.get("SKU"),
                unit=row_dict.get("Unit"),
                quantity=row_dict.get("Quantity"),
                cost=row_dict.get("Cost"),
            )
            for row_dict in (
                self._row_to_dict(vendor_headers, row) for row in vendor_rows
            )
            if row_dict.get("Vendor")
        ]

        store_rows = store_table.get("rows", [])
        store_headers = store_table.get("headers", [])
        store_info = [
            self._build_store_info_from_dict(
                {
                    "store": row_dict.get("Store"),
                    "quantity_on_hand": row_dict.get("Quantity On Hand"),
                }
            )
            for row_dict in (
                self._row_to_dict(store_headers, row) for row in store_rows
            )
            if row_dict.get("Store") is not None or row_dict.get("Quantity On Hand") is not None
        ]

        aliases_value = item_row_dict.get("Aliases", "")
        aliases = self._normalize_aliases(aliases_value)

        return Item(
            id=item_row_dict.get("ID"),
            name=item_row_dict.get("Name"),
            count_unit=item_row_dict.get("Count Unit"),
            category=item_row_dict.get("Category"),
            subcategory=item_row_dict.get("Subcategory"),
            vendor_info=vendor_info,
            store_info=store_info,
            is_active=self._coerce_bool(item_row_dict.get("Active?"), default=True),
            is_inventoried=self._coerce_bool(
                item_row_dict.get("Inventoried?"), default=True
            ),
            notes=item_row_dict.get("Notes"),
            aliases=aliases,
        )

    def from_table(self, table: dict[str, Any]) -> Item:
        """
        Reconstructs an Item from a single flat item table row.

        This is mainly for CSV support. Vendor/store tables are not expected
        here, so vendor_info and store_info default to empty lists.
        """
        headers = table.get("headers", [])
        rows = table.get("rows", [])

        if not rows:
            raise ValueError("Table payload contains no rows.")

        row_dict = self._row_to_dict(headers, rows[0])
        aliases = self._normalize_aliases(row_dict.get("Aliases", ""))

        return Item(
            id=row_dict.get("ID"),
            name=row_dict.get("Name"),
            count_unit=row_dict.get("Count Unit"),
            category=row_dict.get("Category"),
            subcategory=row_dict.get("Subcategory"),
            vendor_info=[],
            store_info=[],
            is_active=self._coerce_bool(row_dict.get("Active?"), default=True),
            is_inventoried=self._coerce_bool(
                row_dict.get("Inventoried?"), default=True
            ),
            notes=row_dict.get("Notes"),
            aliases=aliases,
        )

    # ------------------------------------------------------------------
    # Table builders
    # ------------------------------------------------------------------

    def _item_table(self, item: Item) -> dict[str, Any]:
        return {
            "metadata": {},
            "headers": [
                "ID",
                "Name",
                "Count Unit",
                "Category",
                "Subcategory",
                "Active?",
                "Inventoried?",
                "Notes",
                "Aliases",
            ],
            "rows": [[
                item.id,
                item.name,
                item.count_unit,
                item.category,
                item.subcategory,
                item.is_active,
                item.is_inventoried,
                item.notes,
                ", ".join(item.aliases) if item.aliases else "",
            ]],
        }

    def _vendor_table(self, item: Item) -> dict[str, Any]:
        return {
            "metadata": {},
            "headers": [
                "Item ID",
                "Vendor",
                "SKU",
                "Unit",
                "Quantity",
                "Cost",
            ],
            "rows": [
                [
                    item.id,
                    v.vendor,
                    v.sku,
                    v.unit,
                    v.quantity,
                    v.cost,
                ]
                for v in item.vendor_info
            ],
        }

    def _store_table(self, item: Item) -> dict[str, Any]:
        return {
            "metadata": {},
            "headers": [
                "Item ID",
                "Store",
                "Quantity On Hand",
            ],
            "rows": [
                [
                    item.id,
                    getattr(s, "store", None),
                    s.quantity_on_hand,
                ]
                for s in item.store_info
            ],
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_dict(self, headers: list[Any], row: list[Any]) -> dict[str, Any]:
        normalized_headers = [str(h).strip() if h is not None else "" for h in headers]
        padded_row = list(row) + [None] * max(0, len(normalized_headers) - len(row))
        return dict(zip(normalized_headers, padded_row))

    def _normalize_aliases(self, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]

        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]

        return [str(value).strip()] if str(value).strip() else []

    def _coerce_bool(self, value: Any, default: bool = False) -> bool:
        if value is None:
            return default

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "y", "1"}:
                return True
            if normalized in {"false", "no", "n", "0"}:
                return False

        return default

    def _is_single_table(self, payload: dict[str, Any]) -> bool:
        return isinstance(payload, dict) and "headers" in payload and "rows" in payload

    def _build_store_info_from_dict(self, data: dict[str, Any]) -> StoreItemInfo:
        """
        Handles minor model variation gracefully:
        - if StoreItemInfo supports 'store', pass it
        - otherwise fall back to only quantity_on_hand
        """
        try:
            return StoreItemInfo(
                store=data.get("store"),
                quantity_on_hand=data.get("quantity_on_hand"),
            )
        except TypeError:
            return StoreItemInfo(
                quantity_on_hand=data.get("quantity_on_hand"),
            )