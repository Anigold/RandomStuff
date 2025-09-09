from abc import ABC, abstractmethod
from typing import Any

class BaseSerializer(ABC):
    @abstractmethod
    def get_headers(self) -> list[str]:
        pass

    @abstractmethod
    def to_rows(self, obj: Any) -> list[list[Any]]:
        pass

    @abstractmethod
    def from_rows(self, rows: list[list[Any]], metadata: dict = None) -> Any:
        pass