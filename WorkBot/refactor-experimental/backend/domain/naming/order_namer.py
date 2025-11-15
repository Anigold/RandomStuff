from pathlib import Path
from datetime import datetime
from backend.domain.models import Order
from backend.app.ports.generic import Namer


class OrderFilenameStrategy(Namer[Order]):
    """
    Naming convention for Order files:
    e.g.  Bakery_Sysco_2025-09-21.xlsx
          Downtown_UNFI_2025-09-20.pdf
    """

    def __init__(self, orders_base_dir: Path, uploads_base_dir: Path, archive_dir: Path):
        self._base         = orders_base_dir
        self._upload_base  = uploads_base_dir
        self._archive_base = archive_dir

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
        return f"{obj.vendor}_{obj.store}_{date_str}.{ext}"

    def directory_for(self, order: Order) -> Path:
        return self.base_dir() / order.vendor
    
    def path_for(self, order: Order, *, format: str, category: str | None = None) -> Path:

        if not category:
            return (self.directory_for(order) / self.filename(order, format=format)).resolve()
        if category == 'upload':
            return (self.upload_path_for(order) / self.filename(order, format=format)).resolve()
        if category == 'archive':
            return (self.archive_path_for(order) / self.filename(order, format=format)).resolve()
        if category == 'combined':
            return (None)

    def upload_path_for(self, order: Order) -> Path:
        return self._upload_base / order.vendor
    
    def archive_path_for(self, order: Order) -> Path:
        return self._archive_base / order.vendor
    
    def parse_metadata_for_filename(
        self, *, store: str, vendor: str, date: str | None = None, format: str = "xlsx"
    ) -> Path | str:
        return f"{store}_{vendor}_*.{format}" if (date is None or date == '*') else f"{store}_{vendor}_{date}.{format}"
    
    def parse_filename_for_metadata(self, filename: str) -> dict:
        """Extract store, vendor, and date back from a filename."""
        stem = Path(filename).stem  # remove extension
        try:
            vendor, store, date_str = stem.split("_", maxsplit=2)
        except ValueError:
            return {"store": None, "vendor": None, "date": None}
        return {
            "store":  store,
            "vendor": vendor,
            "date":   date_str,
        }

    def parse_path_metadata(self, path: Path) -> dict[str, str]:
        """
        Combine filename metadata with directory-based vendor info.
        """
        meta = self.parse_filename_for_metadata(path.name)
        if not meta.get("vendor"):
            # infer vendor from parent directory
            meta["vendor"] = path.parent.name
        return meta