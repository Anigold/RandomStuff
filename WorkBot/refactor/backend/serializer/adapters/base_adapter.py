# backend/serializer/adapters/base_adapter.py
from __future__ import annotations
from typing import Type, Dict, Iterable

class BaseAdapter:
    """Adapters tweak tabular data only—no workbook or IO concerns."""
    preferred_format: str = 'excel'

    def modify_headers(self, headers: list[str]) -> list[str]:
        return headers

    def modify_row(self, row: list, item: object | None = None) -> list:
        return row

