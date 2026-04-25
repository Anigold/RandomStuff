from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from backend.domain.models import Transfer, TransferItem
from backend.core.interfaces.serializer import Serializer
from backend.core.interfaces.formatter import BaseFormatter
from backend.infra.logger import Logger

from ..formats import get_formatter


@Logger.attach_logger
class TransferSerializer(Serializer[Transfer]):

    def __init__(self, default_format: str = "xlsx"):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ------------------------------------------------------------------
    # Core protocol
    # ------------------------------------------------------------------

    def dumps(
        self,
        obj: Transfer,
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
            payload = self.to_table(obj)

        else:
            raise ValueError(f"Unsupported format for TransferSerializer: {fmt}")

        return formatter.dumps(payload, context=context)

    def loads(self, data: bytes, format: Optional[str] = None) -> Transfer:
        fmt = (format or self.preferred_format()).lower()
        formatter = self.get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt == "json":
            return self.from_dict(payload)

        if fmt == "xlsx":
            return self.from_workbook(payload)

        if fmt == "csv":
            return self.from_table(payload)

        raise ValueError(f"Unsupported format for TransferSerializer: {fmt}")

    def load_path(self, path: Path, context: dict | None = None) -> Transfer:
        fmt = path.suffix.lstrip(".").lower()
        formatter = self.get_formatter(fmt)
        self.logger.info(context)
        payload = formatter.load_path(path, context=context)
      
        if fmt == "json":
            return self.from_dict(payload)

        if fmt == "xlsx":
            return self.from_workbook(payload)

        if fmt == "csv":
            return self.from_table(payload)

        raise ValueError(f"Unsupported format for TransferSerializer: {fmt}")

    def get_formatter(self, fmt: str) -> BaseFormatter:
        return get_formatter(fmt)

    # ------------------------------------------------------------------
    # Domain <-> dict
    # ------------------------------------------------------------------

    def to_dict(self, transfer: Transfer) -> Dict[str, Any]:
        return {
            "origin": transfer.origin,
            "destination": transfer.destination,
            "transfer_date": transfer.transfer_date,
            "transfer_items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                }
                for item in transfer.transfer_items
            ],
        }

    def from_dict(self, data: Dict[str, Any]) -> Transfer:
        return Transfer(
            origin=data["origin"],
            destination=data["destination"],
            transfer_date=data["transfer_date"],
            transfer_items=[
                TransferItem(
                    name=item["name"],
                    quantity=item["quantity"],
                )
                for item in data.get("transfer_items", [])
            ],
        )

    # ------------------------------------------------------------------
    # Domain <-> tabular
    # ------------------------------------------------------------------

    def to_table(self, transfer: Transfer) -> Dict[str, Any]:
        """
        Single-table representation used for CSV and as the inner table for XLSX.
        """
        return {
            "headers": ["Name", "Quantity"],
            "rows": [
                [item.name, item.quantity]
                for item in transfer.transfer_items
            ],
            "metadata": {
                "origin": transfer.origin,
                "destination": transfer.destination,
                "transfer_date": transfer.transfer_date,
            },
        }

    def from_table(self, table: Dict[str, Any]) -> Transfer:
        metadata = table.get("metadata", {})
        rows = table.get("rows", [])

        return Transfer(
            origin=metadata.get("origin"),
            destination=metadata.get("destination"),
            transfer_date=metadata.get("transfer_date"),
            transfer_items=[
                TransferItem(
                    name=row[0],
                    quantity=row[1],
                )
                for row in rows
                if row and row[0] is not None
            ],
        )

    # ------------------------------------------------------------------
    # Workbook support
    # ------------------------------------------------------------------

    def to_workbook(
        self,
        transfer: Transfer,
        context: dict | None = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Multi-table workbook shape for ExcelFormatter.

        Keeping this as a workbook mapping makes the serializer robust against
        the new Excel formatter behavior, even though Transfer currently only
        needs one logical sheet.
        """
        return {
            "transfer_items": self.to_table(transfer),
        }

    def from_workbook(self, payload: Dict[str, Any]) -> Transfer:
        """
        Accept either:
        - a single table payload
        - a workbook payload containing a 'transfer_items' sheet
        """
        if self._is_single_table(payload):
            return self.from_table(payload)

        if "transfer_items" in payload:
            return self.from_table(payload["transfer_items"])

        # Fallback: if there is exactly one sheet, use it
        if isinstance(payload, dict) and len(payload) == 1:
            return self.from_table(next(iter(payload.values())))

        raise ValueError(
            "Workbook payload does not contain a recognizable transfer table."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_single_table(self, payload: Dict[str, Any]) -> bool:
        return isinstance(payload, dict) and "headers" in payload and "rows" in payload