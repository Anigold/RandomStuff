from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Any, Sequence

from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.repos.ports_generic_repo import Mapper, TableSpec, RecordStore

@dataclass(frozen=True)
class OrderTables:
    orders: TableSpec = TableSpec(
        name="Orders",
        create_sql="""
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT NOT NULL,
            vendor TEXT NOT NULL,
            date TEXT NOT NULL
        )"""
    )
    items: TableSpec = TableSpec(
        name="OrderItems",
        create_sql="""
        CREATE TABLE IF NOT EXISTS OrderItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            sku TEXT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            cost_per REAL,
            total_cost REAL,
            FOREIGN KEY(order_id) REFERENCES Orders(id)
        )"""
    )

class OrderMapper(Mapper[Order]):
    """Defines how to persist/load Order using the generic RecordStore."""
    def __init__(self, store: RecordStore):
        self.store = store
        self.tables = OrderTables()

    def ensure_schema(self) -> None:
        self.store.execute(self.tables.orders.create_sql)
        self.store.execute(self.tables.items.create_sql)

    def insert(self, obj: Order) -> int:
        order_id = self.store.execute(
            "INSERT INTO Orders (store, vendor, date) VALUES (?, ?, ?)",
            (obj.store, obj.vendor, obj.date)
        )
        if obj.items:
            rows: list[tuple[Any, ...]] = [
                (order_id, it.sku, it.name, float(it.quantity or 0), float(getattr(it, "cost_per", 0) or 0), float(getattr(it, "total_cost", 0) or 0))
                for it in obj.items
            ]
            self.store.executemany(
                "INSERT INTO OrderItems (order_id, sku, name, quantity, cost_per, total_cost) VALUES (?, ?, ?, ?, ?, ?)",
                rows
            )
        return int(order_id)

    # Optional — only if you need reads via repo:
    def row_to_obj(self, row: Sequence[Any]) -> Order:
        # row: (id, store, vendor, date)
        _, store, vendor, date = row
        items_rows = self.store.query_all("SELECT sku,name,quantity,cost_per,total_cost FROM OrderItems WHERE order_id = ?", (_ ,))
        items = [OrderItem(*map(str, r[:2]), str(r[2]), str(r[3]), str(r[4])) for r in items_rows]
        return Order(store=store, vendor=vendor, date=date, items=items)
