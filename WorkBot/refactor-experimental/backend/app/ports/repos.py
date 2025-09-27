from __future__ import annotations
from typing import Protocol
from backend.domain.models import Order

class OrderRepository(Protocol):
    def save_order(self, order: Order) -> int: ...
    # Optionally add: find_by_id, list_recent, etc.