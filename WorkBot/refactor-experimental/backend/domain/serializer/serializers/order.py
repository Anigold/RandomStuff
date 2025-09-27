from pathlib import Path
from typing import Optional
from backend.domain.models import Order, OrderItem
from backend.app.ports.generic import Serializer
from ..formats import get_formatter


class OrderSerializer(Serializer[Order]):
    """
    Domain serializer: maps Order <-> dict.
    Delegates bytes conversion to a pluggable Formatter via the registry.
    """

    def __init__(self, default_format: str = 'xlsx'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ---- Core protocol ----
    def dumps(self, obj: Order, format: Optional[str] = None) -> bytes:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)

        order_dict = self.to_dict(obj)
        order_tablular = self._to_table(order_dict)
      

        return formatter.dumps(order_tablular)

    def loads(self, data: bytes, format: Optional[str] = None) -> Order:
        fmt = format or self.preferred_format()
        formatter = get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload) 
        else:
            return self.from_dict(payload)

    def load_path(self, path: Path) -> Order:

        fmt = path.suffix.lstrip(".").lower()
        formatter = get_formatter(fmt)
        payload = formatter.load_path(path)
        return self.from_dict(payload)

    # ---- Domain <-> dict ----
    def to_dict(self, order: Order) -> dict:
        out = {
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

        return out

    def from_dict(self, data: dict) -> Order:
        meta = data.get("metadata", {})
        items = [
            OrderItem(
                sku=i.get("sku", ""),
                name=i.get("name", ""),
                quantity=i.get("quantity", 0),
                cost_per=i.get("cost_per", 0),
                total_cost=i.get("total_cost", 0),
            )
            for i in data.get("items", [])
        ]
        return Order(
            store=meta.get("store", ""),
            vendor=meta.get("vendor", ""),
            date=meta.get("date", ""),
            items=items,
        )


    def _to_table(self, order_dict: dict, context: dict | None = None) -> dict:
        metadata = {
            'store': order_dict.get('store', ''),
            'vendor': order_dict.get('vendor'),
            'date': order_dict.get('date', '')
        }

        headers = ['SKU', 'Name', 'Quantity', 'Cost Per', 'Total Cost']
        rows = [
            [i['sku'], i['name'], i['quantity'], i.get('cost_per', 0.0), i.get('total_cost', 0.0)]
            for i in order_dict.get('items', [])
        ]
        return {'metadata': metadata, 'headers': headers, 'rows': rows}
    
    def from_table(self, table: dict) -> Order:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        meta = table.get("metadata", {})   # always pass it through

        items = []
        for row in rows:
            item = dict(zip(headers, row))
            items.append(item)

        data = {
            "metadata": meta,   # preserve metadata
            "items": items,
        }

        return self.from_dict(data)