from pathlib import Path
from typing import Generic, TypeVar, Optional
from abc import ABC, abstractmethod
from backend.infra.logger import Logger

T = TypeVar("T")


@Logger.attach_logger
class BaseFormatter(Generic[T], ABC):
    """
    Base class for formatters with file support.

    Supported payload shapes:

    Single table:
        {
            "headers": ["col1", "col2", ...],
            "rows": [
                ["a", "b", ...],
                ["c", "d", ...],
            ],
            "metadata": {...}   # optional
        }

    Multi-table / workbook:
        {
            "sheet_name_1": {
                "headers": [...],
                "rows": [...],
                "metadata": {...}
            },
            "sheet_name_2": {
                "headers": [...],
                "rows": [...],
                "metadata": {...}
            }
        }

    Not every formatter must support both shapes.
    """

    @abstractmethod
    def dumps(self, obj: T, format: Optional[str] = None, context: dict | None = None) -> bytes:
        ...

    @abstractmethod
    def loads(self, data: bytes, format: Optional[str] = None) -> T:
        ...

    def load_path(self, path: Path, context: dict | None = None) -> T:
        """Default: read bytes then call .loads(). Can be overridden."""
        with open(path, "rb") as f:
            return self.loads(f.read())