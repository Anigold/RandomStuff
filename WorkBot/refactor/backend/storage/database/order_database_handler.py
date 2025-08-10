from __future__ import annotations
from typing import Optional
from .database_handler import DatabaseHandler

class OrderDatabaseHandler(DatabaseHandler):
    def get_all_orders_summary(self, limit: int = 100, offset: int = 0) -> list[dict]:
        query = """
            SELECT
                o.id                          AS id,
                o.date                        AS date,
                COALESCE(o.placed, 0)         AS placed,
                s.store_name                  AS store_name,
                v.name                        AS vendor_name,
                COUNT(oi.id)                  AS item_count,
                COALESCE(SUM(oi.quantity * oi.cost_per), 0) AS total_cost
            FROM Orders o
            JOIN Stores  s ON s.id = o.store_id
            JOIN Vendors v ON v.id = o.vendor_id
            LEFT JOIN OrderItems oi ON oi.order_id = o.id
            GROUP BY o.id, o.date, o.placed, s.store_name, v.name
            ORDER BY o.date DESC, o.id DESC
            LIMIT ? OFFSET ?
        """
        return self.fetch_all(query, (limit, offset))

    def get_order_summary_by_id(self, order_id: int) -> Optional[dict]:
        query = """
            SELECT
                o.id                          AS id,
                o.date                        AS date,
                COALESCE(o.placed, 0)         AS placed,
                s.store_name                  AS store_name,
                v.name                        AS vendor_name,
                COALESCE(SUM(oi.quantity * oi.cost_per), 0) AS total_cost
            FROM Orders o
            JOIN Stores  s ON s.id = o.store_id
            JOIN Vendors v ON v.id = o.vendor_id
            LEFT JOIN OrderItems oi ON oi.order_id = o.id
            WHERE o.id = ?
            GROUP BY o.id, o.date, o.placed, s.store_name, v.name
        """
        return self.fetch_one(query, (order_id,))

    def get_order_items(self, order_id: int) -> list[dict]:
        query = """
            SELECT
                i.id         AS item_id,
                i.item_name  AS name,
                oi.quantity  AS quantity,
                oi.cost_per  AS cost_per
            FROM OrderItems oi
            JOIN Items i ON i.id = oi.item_id
            WHERE oi.order_id = ?
            ORDER BY i.item_name ASC
        """
        return self.fetch_all(query, (order_id,))

    def create_order(self, store_id: int, vendor_id: int, date: str) -> int:
        # Unique on (store_id, vendor_id, date)? If so, this will raise on dup (which is good).
        query = "INSERT INTO Orders (store_id, vendor_id, date) VALUES (?, ?, ?)"
        return self.execute(query, (store_id, vendor_id, date))  # lastrowid

    def add_order_items(self, order_id: int, items: list[dict]) -> None:
        # items: [{"item_id": int, "quantity": float, "cost_per": float}, ...]
        query = "INSERT INTO OrderItems (order_id, item_id, quantity, cost_per) VALUES (?, ?, ?, ?)"
        params = [(order_id, it["item_id"], it["quantity"], it["cost_per"]) for it in items]
        self.execute_many(query, params)

    def update_order_item(self, order_id: int, item_id: int, quantity: float, cost_per: float) -> None:
        query = "UPDATE OrderItems SET quantity = ?, cost_per = ? WHERE order_id = ? AND item_id = ?"
        self.execute(query, (quantity, cost_per, order_id, item_id))

    def delete_order_item(self, order_id: int, item_id: int) -> None:
        query = "DELETE FROM OrderItems WHERE order_id = ? AND item_id = ?"
        self.execute(query, (order_id, item_id))
