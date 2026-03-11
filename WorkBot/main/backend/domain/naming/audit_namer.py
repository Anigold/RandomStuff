from pathlib import Path
from datetime import datetime
from backend.domain.models import Audit
from backend.core.interfaces.namer import Namer


class AuditFilenameStrategy(Namer[Audit]):
    """
    Naming convention for Audit files:
    """

    def __init__(self, audits_base_dir: Path, archive_dir: Path):
        self._base = audits_base_dir
        self._archive = archive_dir

    def base_dir(self) -> Path:
        """Return the base directory where all order files live."""
        return self._base

    def filename(self, obj: Audit, format: str) -> str:
        """Build filename like Store_Vendor_Date.ext"""
        date_str = (
            obj.date if isinstance(obj.date, str)
            else datetime.strftime(obj.date, "%Y-%m-%d")
        )
        ext = "xlsx" if format in ("excel", "xlsx") else format
        return f'{obj.store}_{obj.audit_type}_{date_str}.{ext}'

    def directory_for(self, audit: Audit) -> Path:
        return self.base_dir()
    
    def archive_path_for(self, audit: Audit) -> Path:
        return self._archive
    
    def path_for(self, audit: Audit, *, format: str, category: str | None = None) -> Path:

        audit_dir = self.directory_for(audit)
        audit_filename = self.filename(audit, format=format)

        if not category:
            return (audit_dir / audit_filename).resolve()
        if category == 'archive':
            return (self.archive_path_for(audit) / audit_filename).resolve()
        
        return (audit_dir / audit_filename).resolve()
    # def upload_path_for(self, order: Order) -> Path:
    #     return self._upload_base / order.vendor
    
    # def parse_metadata_for_filename(
    #     self, *, store: str, vendor: str, date: str | None = None, format: str = "xlsx"
    # ) -> Path | str:
    #     return f"{store}_{vendor}_*.{format}" if (date is None or date == '*') else f"{store}_{vendor}_{date}.{format}"
    
    
    def parse_filename_for_metadata(self, filename: str) -> dict:
        """
        Extract {store, audit_type, date} from:
        {store}_{audit_type}_{YYYY-MM-DD}.{ext}

        Robust to stores containing underscores by taking the last two underscore
        segments as audit_type and date, and joining the rest back into store.
        """
        stem = Path(filename).name  # allow full path input
        stem = Path(stem).stem      # remove extension

        parts = stem.split("_")
        if len(parts) < 3:
            return {"store": None, "audit_type": None, "date": None}

        # store may contain underscores, so grab from the left
        store = "_".join(parts[:-2])
        audit_type = parts[-2]
        date_str = parts[-1]

        return {
            "store": store or None,
            "audit_type": audit_type or None,
            "date": date_str or None,
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