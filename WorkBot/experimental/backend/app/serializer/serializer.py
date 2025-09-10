# backend/app/serialization/core/router.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, List, Dict
from backend.app.files.ports_generic import Serializer

@dataclass
class DomainRouterSerializer(Serializer):
    """Single, unified serializer that routes by type / path."""
    modules: List[DomainModule] = field(default_factory=list)

    def _pick_for_obj(self, obj: Any) -> DomainModule:
        for m in self.modules:
            if m.supports_type(obj):
                return m
        raise TypeError(f"No serializer module registered for type {type(obj)!r}")

    def _pick_for_path(self, path: Path) -> DomainModule:
        for m in self.modules:
            if m.supports_path(path):
                return m
        raise TypeError(f"No serializer module registered that supports path {path.name!r}")

    def dumps(self, obj: Any, *, format: Optional[str] = None, context: dict | None = None) -> bytes:
        m = self._pick_for_obj(obj)
        fmt = (format or m.preferred_format()).lower()
        return m.to_bytes(obj, format=fmt, context=context or {})

    def loads(self, data: bytes, *, format: Optional[str] = None, context: dict | None = None) -> Any:
        # Try every module (use explicit format if provided)
        for m in self.modules:
            fmt = (format or m.preferred_format()).lower()
            if fmt in m.supported_formats():
                try:
                    return m.from_bytes(data, format=fmt, context=context or {})
                except Exception:
                    continue
        raise ValueError("No module could parse bytes for the given format")

    def load_path(self, path: Path, *, context: dict | None = None) -> Any:
        m = self._pick_for_path(path)
        return m.from_path(path, context=context or {})
