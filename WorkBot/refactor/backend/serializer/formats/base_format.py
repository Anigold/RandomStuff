from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseFormat(ABC):
    """
    Abstract base class for all format strategies.
    Defines the interface for reading and writing tabular data.
    """

    registry = {}  # Maps vendor name to format class

    @classmethod
    def register(cls, vendor: str):
        def decorator(format_cls):
            cls.registry[vendor] = format_cls
            return format_cls
        return decorator

    @classmethod
    def get_format_for_vendor(cls, vendor: str):
        try:
            return cls.registry[vendor]()
        except KeyError:
            raise ValueError(f"No format registered for vendor: {vendor}")

    @abstractmethod
    def write(self, headers: list[str], rows: list[list[Any]]) -> Any:
        """Return a writable object (Workbook, str, etc) given headers and rows."""
        pass

    @abstractmethod
    def read(self, file_path: Path) -> list[list[Any]]:
        """Read a file and return a list of rows (with headers excluded)."""
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Format", "").lower()
