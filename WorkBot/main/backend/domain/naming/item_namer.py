from pathlib import Path
from backend.domain.models import Item
from backend.core.interfaces.namer import Namer


class ItemFilenameStrategy(Namer[Item]):

    def __init__(self, base: Path):
        self._base = base

    def base_dir(self) -> Path:
        """Return the base directory where all item files live."""
        return self._base

    def filename(self, obj: Item, *, format: str) -> str:
        """
        Use the stable item ID as the filename so renaming an item
        does not change its persisted file path.
        """
        ext = "json" if format in ("json", "yaml") else format
        return f"{obj.id}.{ext}"

    def directory_for(self, item: Item) -> Path:
        """Items do not need subdirectories; keep everything flat."""
        return self.base_dir()

    def path_for(self, item: Item, *, format: str) -> Path:
        return (self.directory_for(item) / self.filename(item, format=format)).resolve()

    def parse_filename_for_metadata(self, filename: str) -> dict:
        """
        Extract minimal metadata from the filename for adapter/serializer use.
        """
        path = Path(filename)
        return {
            "id": path.stem,
            "format": path.suffix.lstrip(".").lower(),
            "filename": path.name,
        }

    def parse_path_metadata(self, path: Path) -> dict:
        """
        GenericFileAdapter.find() relies on this for file discovery filtering.
        """
        meta = self.parse_filename_for_metadata(path.name)
        meta["path"] = str(path)
        return meta