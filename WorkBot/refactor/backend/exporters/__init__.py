from abc import ABC, abstractmethod

_exporter_registry = {}

def register_exporter(domain_cls, fmt: str):
    def decorator(exporter_cls):
        _exporter_registry[(domain_cls, fmt.lower())] = exporter_cls()
        return exporter_cls
    return decorator

def get_exporter(obj, fmt: str):
    key = (type(obj), fmt.lower())
    if key not in _exporter_registry:
        raise ValueError(f"No exporter for {type(obj).__name__} to {fmt}")
    return _exporter_registry[key]

class Exporter(ABC):
    @abstractmethod
    def export(self, obj, path: str) -> None:
        pass
