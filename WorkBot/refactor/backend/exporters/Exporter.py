from abc import ABC, abstractmethod
from typing import Any
from .adapters import ExportAdapter

class Exporter(ABC):

    _EXPORTER_REGISTRY = {}

    @classmethod
    def register_exporter(cls, domain_cls, fmt: str):
        def decorator(exporter_cls):
            cls._EXPORTER_REGISTRY[(domain_cls, fmt.lower())] = exporter_cls()
            return exporter_cls
        return decorator

    @classmethod
    def get_exporter(cls, domain_cls, fmt: str):
        key = (domain_cls, fmt.lower())
        if key not in cls._EXPORTER_REGISTRY:
            raise ValueError(f"No exporter for {domain_cls.__name__} to {fmt}")
        return cls._EXPORTER_REGISTRY[key]
    
    @abstractmethod
    def export(self, obj, adapter: ExportAdapter = None, context: dict = None) -> Any:
        pass
