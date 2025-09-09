# base_format.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseFormat(ABC):
    
    @abstractmethod
    def write(self, headers: list[str], rows: list[list[Any]]) -> Any: 
        ...

    @abstractmethod
    def read(self, file_path: Path) -> list[list[Any]]: 
        ...
