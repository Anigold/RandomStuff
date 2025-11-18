from pathlib import Path
from datetime import datetime
from backend.domain.models import Transfer
from backend.core.interfaces.namer import Namer


class TransferFilenameStrategy(Namer[Transfer]):
    """
    Naming convention for Transfer files:
    e.g.  Bakery_Collegetown_2025-09-21.xlsx
          Downtown_Triphammer_2025-09-20.pdf
    """

    def __init__(self, transfers_base_dir: Path, archive_dir: Path):
        self._base = transfers_base_dir
        self._archive = archive_dir

    def base_dir(self) -> Path:
        """Return the base directory where all order files live."""
        return self._base

    def filename(self, obj: Transfer, format: str) -> str:
        """Build filename like Store_Vendor_Date.ext"""
        date_str = (
            obj.transfer_date if isinstance(obj.transfer_date, str)
            else datetime.strftime(obj.transfer_date, "%Y-%m-%d")
        )
        ext = "xlsx" if format in ("excel", "xlsx") else format
        return f"{obj.origin}_{obj.destination}_{date_str}.{ext}"

    def directory_for(self, transfer: Transfer) -> Path:
        return self.base_dir()
    
    def archive_path_for(self, transfer: Transfer) -> Path:
        return self._archive
    
    def path_for(self, transfer: Transfer, *, format: str, category: str | None = None) -> Path:

        if not category:
            return (self.directory_for(transfer) / self.filename(transfer, format=format)).resolve()
        if category == 'archive':
            return (self.archive_path_for(transfer) / self.filename(transfer, format=format)).resolve()
        
        return (self.directory_for(transfer) / self.filename(transfer, format=format)).resolve()
    # def upload_path_for(self, order: Order) -> Path:
    #     return self._upload_base / order.vendor
    
    # def parse_metadata_for_filename(
    #     self, *, store: str, vendor: str, date: str | None = None, format: str = "xlsx"
    # ) -> Path | str:
    #     return f"{store}_{vendor}_*.{format}" if (date is None or date == '*') else f"{store}_{vendor}_{date}.{format}"
    
    
    def parse_filename_for_metadata(self, filename: str) -> dict:
        """Extract store, vendor, and date back from a filename."""
        stem = Path(filename).stem  # remove extension
        try:
            origin, destination, date_str = stem.split("_", maxsplit=2)
        except ValueError:
            return {"origin": None, "destination": None, "date": None}
        return {
            "origin": origin,
            "destination": destination,
            "transfer_date": date_str,
        }

    # def parse_path_metadata(self, path: Path) -> dict[str, str]:
    #     """
    #     Combine filename metadata with directory-based vendor info.
    #     """
    #     meta = self.parse_filename_for_metadata(path.name)
    #     if not meta.get("vendor"):
    #         # infer vendor from parent directory
    #         meta["vendor"] = path.parent.name
    #     return meta