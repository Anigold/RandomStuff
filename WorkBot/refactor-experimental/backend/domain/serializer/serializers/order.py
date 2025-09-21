from pathlib import Path
from typing import Optional
from backend.domain.models.order import Order, OrderItem
from backend.app.ports.generic import Serializer
from ..formats import get_formatter


class OrderSerializer(Serializer[Order]):
    """
    Domain serializer: maps Order <-> dict.
    Delegates bytes conversion to a pluggable Formatter via the registry.
    """

    def __init__(self, default_format: str = "xlsx"):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ---- Core protocol ----
    def dumps(self, obj: Order, format: Optional[str] = None) -> bytes:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)
        return formatter.dumps(self.to_dict(obj))

    def loads(self, data: bytes, format: Optional[str] = None) -> Order:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)
        payload = formatter.loads(data)
        return self.from_dict(payload)

    def load_path(self, path: Path) -> Order:
        fmt = path.suffix.lstrip(".").lower()
        formatter = get_formatter(fmt)
        payload = formatter.load_path(path)
        return self.from_dict(payload)

    # ---- Domain <-> dict ----
    def to_dict(self, order: Order) -> dict:
        return {
            "store": order.store,
            "vendor": order.vendor,
            "date": order.date,
            "items": [
                {
                    "sku": i.sku,
                    "name": i.name,
                    "quantity": i.quantity,
                    "cost_per": i.cost_per,
                    "total_cost": i.total_cost,
                }
                for i in order.items
            ],
        }

    def from_dict(self, data: dict) -> Order:
        items = [
            OrderItem(
                sku=i.get("sku"),
                name=i.get("name"),
                quantity=i.get("quantity"),
                cost_per=i.get("cost_per"),
                total_cost=i.get("total_cost"),
            )
            for i in data.get("items", [])
        ]
        return Order(
            store=data["store"],
            vendor=data["vendor"],
            date=data["date"],
            items=items,
        )
