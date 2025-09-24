# backend/domain/serializers/vendor_namer.py

from pathlib import Path
from backend.domain.models.vendor import Vendor
from backend.app.ports.generic import Namer
import re

class VendorFilenameStrategy(Namer[Vendor]):
    """
    Naming convention for Vendor files:
    e.g.  vendors/Sysco.json
          vendors/UNFI.yaml
    """

    def __init__(self, base: Path):
        self._base = base

    def base_dir(self) -> Path:
        """Return the base directory where all vendor files live."""
        return self._base

    def _sanitize(self, name: str) -> str:
        safe = name.replace("&", "and")
        safe = safe.replace(" ", "_")
        safe = re.sub(r"[^A-Za-z0-9_.-]", "", safe)  # strip anything else risky
        return safe

    def filename(self, obj: Vendor, *, format: str) -> str:
        ext = "json" if format in ("json", "yaml") else format
        return f"{self._sanitize(obj.name)}.{ext}"

    def directory_for(self, vendor: Vendor) -> Path:
        """Vendors do not need subdirectories; keep everything flat."""
        return self.base_dir()

    def path_for(self, vendor: Vendor, *, format: str) -> Path:
        return (self.directory_for(vendor) / self.filename(vendor, format=format)).resolve()

    def parse_metadata(self, filename: str) -> dict[str, str]:
        """Extract vendor name from a filename."""
        stem = Path(filename).stem
        return {"name": stem.replace("_", " ")}
