from __future__ import annotations
import uuid, traceback
from dataclasses import dataclass, field
from typing import List, Callable, Optional

@dataclass
class ErrorEvent:
    id: str                = field(default_factory=lambda: str(uuid.uuid4()))
    type: str              = ""
    message: str           = ""
    context: Optional[str] = None
    severity: str          = "ERROR"
    trace: Optional[str]   = None
    layer: Optional[str]   = None   # "infra", "repo", "service", "workbot"


class ErrorBus:
    _subscribers: List[Callable[[ErrorEvent], None]] = []

    @classmethod
    def subscribe(cls, handler: Callable[[ErrorEvent], None]):
        cls._subscribers.append(handler)

    @classmethod
    def unsubscribe(cls, handler: Callable[[ErrorEvent], None]):
        if handler in cls._subscribers:
            cls._subscribers.remove(handler)
            
    @classmethod
    def emit(cls, event: ErrorEvent):
        for handler in list(cls._subscribers):
            try:
                handler(event)
            except Exception:
                pass   # Subscribers never interfere with each other





