from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

ToDoKind = Literal['vendor_order', 'custom']

@dataclass
class ToDo:
    kind: ToDoKind
    title: str
    done: bool = False
    vendor:   Optional[str] = None
    store:    Optional[str] = None
    notes:    Optional[str] = None
    due_time: Optional[str] = None # 24h "HH:MM" local-time string (e.g. "15:00")
    due_at:   Optional[str] = None # ISO local datetime "YYYY-MM-DDTHH:MM" (filled by coordinator when date is known)

    # Deterministic key for idempotent merge
    def key(self) -> tuple:
        def canon(x): return (x or "").strip()
        return (canon(self.kind), canon(self.vendor), canon(self.store))
