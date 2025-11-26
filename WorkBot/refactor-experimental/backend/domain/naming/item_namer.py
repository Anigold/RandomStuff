from pathlib import Path
from backend.domain.models import Item
from backend.core.interfaces.namer import Namer
import re

class ItemFilenameStrategy(Namer[Item]):

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

    def filename(self, obj: Item, *, format: str) -> str:
        ext = "json" if format in ("json", "yaml") else format
        return f"{self._sanitize(obj.name)}.{ext}"

    def directory_for(self, store: Item) -> Path:
        """Stores do not need subdirectories; keep everything flat."""
        return self.base_dir()

    def path_for(self, item: Item, *, format: str) -> Path:
        return (self.directory_for(item) / self.filename(item, format=format)).resolve()

    def parse_filename_for_metadata(self, filename: str) -> dict[str, str]:
        """Extract store name from a filename."""
        stem = Path(filename).stem
        return {"name": stem.replace("_", " ")}
