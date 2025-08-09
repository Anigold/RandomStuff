# backend/serializer/adapters/base_adapter.py
from __future__ import annotations
from typing import Type, Dict, Iterable

class BaseAdapter:
    """Adapters tweak tabular data only—no workbook or IO concerns."""
    _REGISTRY: Dict[str, Type["BaseAdapter"]] = {}
    preferred_format: str = "excel"  # "excel" | "csv" | ...

    # ── Registration (store CLASS; instantiate on get) ───────────────────
    @classmethod
    def register(cls, vendor: str):
        def deco(adapter_cls: Type["BaseAdapter"]):
            cls._REGISTRY[cls._vn(vendor)] = adapter_cls
            return adapter_cls
        return deco

    @classmethod
    def get_adapter(cls, vendor: str) -> "BaseAdapter | None":
        klass = cls._REGISTRY.get(cls._vn(vendor))
        return klass() if klass else None

    @staticmethod
    def _vn(s: str) -> str:
        return " ".join(s.split()).strip().lower()

    @classmethod
    def vendors(cls) -> Iterable[str]:
        return tuple(sorted(cls._REGISTRY.keys()))

    # ── Data-shaping hooks (override as needed) ──────────────────────────
    def modify_headers(self, headers: list[str]) -> list[str]:
        return headers

    def modify_row(self, row: list, item: object | None = None) -> list:
        return row

    # Convenience
    @classmethod
    def get_preferred_format(cls, vendor: str) -> str:
        a = cls.get_adapter(vendor)
        return a.preferred_format if a else "excel"
