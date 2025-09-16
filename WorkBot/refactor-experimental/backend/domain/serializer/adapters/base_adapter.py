# backend/serializer/adapters/base_adapter.py
from __future__ import annotations
from typing import Optional

class BaseAdapter:

    preferred_format: str = 'excel'
    preferred_extension: Optional[str] = None

    def modify_headers(self, headers: list[str]) -> list[str]:
        return headers

    def modify_row(self, row: list, item: object | None = None) -> list:
        return row

    def resolve_extension(self, context: dict | None = None) -> Optional[str]:
        return self.preferred_extension