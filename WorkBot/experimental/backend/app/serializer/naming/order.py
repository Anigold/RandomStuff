from pathlib import Path
from typing import Any
from backend.models.order import Order
from backend.app.files.ports_generic import Namer

class OrderNamer(Namer[Order]):
    """
    Example filename: 2025-09-09 - Store - Vendor.xlsx
    If your date is 'YYYYMMDD', adjust accordingly.
    """
    def __init__(self, base: Path):
        self._base = base

    def base_dir(self) -> Path:
        return self._base

    def filename(self, obj: Order, *, format: str) -> str:
        ext = "xlsx" if format in ("excel", "xlsx") else format
        date = obj.date or "unknown"
        return f"{date} - {obj.store} - {obj.vendor}.{ext}"

    def parse_metadata(self, filename: str) -> dict[str, Any]:
        stem = Path(filename).stem
        try:
            date, store, vendor = [s.strip() for s in stem.split(" - ", 2)]
            return {"date": date, "store": store, "vendor": vendor}
        except Exception:
            return {}
