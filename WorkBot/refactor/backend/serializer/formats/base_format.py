from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseFormat(ABC):
    """
    Abstract base class for all format strategies.
    Defines the interface for reading and writing tabular data.
    """

    @abstractmethod
    def write(self, headers: list[str], rows: list[list[Any]]) -> Any:
        """Return a writable object (Workbook, str, etc) given headers and rows."""
        pass

    @abstractmethod
    def read(self, file_path: Path) -> list[list[Any]]:
        """Read a file and return a list of rows (with headers excluded)."""
        pass
