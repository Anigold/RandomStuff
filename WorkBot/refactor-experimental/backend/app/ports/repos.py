from __future__ import annotations
from typing import Protocol
from backend.domain.models import Order, Vendor
from backend.app.ports.generic import Repository


class OrderRepository(Protocol):
    def save_order(self, order: Order) -> int: ...
    # Optionally add: find_by_id, list_recent, etc.


class VendorRepository(Repository[Vendor], Protocol):
    # Add specific lookups here (e.g. find_by_contact_email)
    ...