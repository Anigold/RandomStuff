# backend/app/serialization/modules/orders.py
from __future__ import annotations
from pathlib import Path
from io import BytesIO
from typing import Any, Optional

from backend.models.order import Order
# legacy pieces (kept, just namespaced)
from backend.serializer.serializers.order_serializer import OrderSerializer           # rows<->Order  :contentReference[oaicite:7]{index=7}
from backend.serializer.adapters.base_adapter import BaseAdapter as ExportProfile   # profile       :contentReference[oaicite:8]{index=8}
from backend.serializer.formats.excel_format import ExcelFormat                     # Excel I/O     :contentReference[oaicite:9]{index=9}
from backend.serializer.filename_strategies.order_filename_strategy import (
    OrderFilenameStrategy                                                           # filenames     :contentReference[oaicite:10]{index=10}
)

class OrdersModule:
    """DomainModule implementation for Order objects."""

    # --- detection ---
    def supports_type(self, obj: Any) -> bool:
        return isinstance(obj, Order)

    def supports_path(self, path: Path) -> bool:
        # be liberal: if .xlsx and filename parses as order, we support
        if path.suffix.lower() == ".xlsx":
            try:
                OrderFilenameStrategy().parse(path.name)   # vendor/store/date
                return True
            except Exception:
                return True  # still allow .xlsx; context can fill metadata
        return False

    # --- formats ---
    def preferred_format(self) -> str:
        return "xlsx"

    def supported_formats(self) -> set[str]:
        return {"xlsx", "excel"}

    # --- serialization ---
    def to_bytes(self, obj: Order, *, format: str, context: dict) -> bytes:
        if format not in self.supported_formats():
            raise ValueError(f"Unsupported orders format: {format}")
        profile: ExportProfile | None = context.get("profile")
        ser   = OrderSerializer()                    # rows<->domain  :contentReference[oaicite:11]{index=11}
        excel = ExcelFormat()                        # tabular I/O     :contentReference[oaicite:12]{index=12}

        headers = ser.get_headers(adapter=profile)   # profile can modify headers
        rows    = ser.to_rows(obj)
        wb      = excel.write(headers, rows)

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def from_bytes(self, data: bytes, *, format: str, context: dict) -> Order:
        if format not in self.supported_formats():
            raise ValueError(f"Unsupported orders format: {format}")
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
            tmp.write(data); tmp.flush()
            return self.from_path(Path(tmp.name), context=context)

    def from_path(self, path: Path, *, context: dict) -> Order:
        excel = ExcelFormat()
        rows  = excel.read(path)                     # rows from Excel :contentReference[oaicite:13]{index=13}

        # Prefer explicit context; otherwise try legacy filename parse
        metadata = dict(context.get("metadata", {}) or {})
        if not {"vendor","store","date"} <= metadata.keys():
            try:
                meta = OrderFilenameStrategy().parse(path.name)       # vendor/store/date  :contentReference[oaicite:14]{index=14}
                metadata = {**meta, **metadata}
            except Exception:
                pass

        ser = OrderSerializer()
        return ser.from_rows(rows, metadata=metadata)  # rows->Order  :contentReference[oaicite:15]{index=15}

    # --- naming ---
    def filename_for(self, obj: Order, *, format: str, context: dict) -> str:
        # allow profile to override extension (e.g., txt) via preferred_extension
        profile: ExportProfile | None = context.get("profile")
        ext = (profile.resolve_extension(context) if profile else None) or format
        return OrderFilenameStrategy().format(obj, extension=ext)      # legacy strategy  :contentReference[oaicite:16]{index=16}
