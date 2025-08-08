from typing import Any
from backend.models.order import Order, OrderItem
from .base_serializer import BaseSerializer

class OrderSerializer(BaseSerializer):
    DEFAULT_HEADERS = ["SKU", "Name", "Quantity", "Cost Per", "Total Cost"]

    def __init__(self, adapter: BaseSerializer = None):
        self.adapter = adapter

    def get_headers(self) -> list[str]:
        if self.adapter:
            return self.adapter.modify_headers(self.DEFAULT_HEADERS)
        return self.DEFAULT_HEADERS

    def to_rows(self, order: Order) -> list[list[Any]]:
        rows = []
        for item in order.items:
            row = [item.sku, item.name, item.quantity, item.cost_per, item.total_cost]
            if self.adapter:
                row = self.adapter.modify_row(row, item=item)
            rows.append(row)
        return rows

    def from_rows(self, rows: list[list[Any]], metadata: dict = None) -> Order:
        metadata = metadata or {}
        vendor = metadata.get("vendor")
        store = metadata.get("store")
        date = metadata.get("date")

        order = Order(store=store, vendor=vendor, date=date)
        for row in rows:
            sku, name, quantity, cost_per, total_cost = row
            item = OrderItem(sku, name, quantity, cost_per, total_cost)
            order.items.append(item)
        return order
