from pathlib import Path
from datetime import datetime
from backend.domain.models.order import Order
from backend.app.ports.generic import Namer


class OrderFilenameStrategy(Namer[Order]):
    """
    Naming convention for Order files:
    e.g.  Bakery_Sysco_2025-09-21.xlsx
          Downtown_UNFI_2025-09-20.pdf
    """

    def __init__(self, base: Path):
        self._base = base

    def base_dir(self) -> Path:
        """Return the base directory where all order files live."""
        return self._base

    def filename(self, obj: Order, format: str) -> str:
        """Build filename like Store_Vendor_Date.ext"""
        date_str = (
            obj.date if isinstance(obj.date, str)
            else datetime.strftime(obj.date, "%Y-%m-%d")
        )
        ext = "xlsx" if format in ("excel", "xlsx") else format
        return f"{obj.store}_{obj.vendor}_{date_str}.{ext}"

    def directory_for(self, order: Order) -> Path:
        # Sort by vendor name
        return self.base_dir() / order.vendor
    
    def path_for(self, order: Order, *, format: str) -> Path:
        return (self.directory_for(order) / self.filename(order, format=format)).resolve()
    
    def parse_metadata(self, filename: str) -> dict:
        """Extract store, vendor, and date back from a filename."""
        stem = Path(filename).stem  # remove extension
        try:
            store, vendor, date_str = stem.split("_", maxsplit=2)
        except ValueError:
            return {"store": None, "vendor": None, "date": None}
        return {
            "store":  store,
            "vendor": vendor,
            "date":   date_str,
        }
