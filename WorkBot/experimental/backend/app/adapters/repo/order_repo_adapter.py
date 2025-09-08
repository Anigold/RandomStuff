# backend/app/adapters/repositories/order_repository_adapter.py
from __future__ import annotations
from backend.app.ports import OrderRepository
from backend.models.order import Order

class OrderRepositoryAdapter(OrderRepository):
    """
    Temporary no-op adapter for the OrderRepository port.
    Provides the right interface so OrderServices can be initialized,
    but doesn't persist anything yet.
    """

    def __init__(self) -> None:
        # You can stash in-memory state here if needed for testing
        self._store: dict[int, Order] = {}
        self._counter: int = 0

    def save_order(self, order: Order) -> int:
        """
        Pretend to persist an order.
        Returns a fake integer ID.
        """
        self._counter += 1
        self._store[self._counter] = order
        return self._counter
