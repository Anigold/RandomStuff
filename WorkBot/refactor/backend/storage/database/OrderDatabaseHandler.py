from .DatabaseHandler import DatabaseHandler
from backend.models.Order import Order

class OrderDatabaseHandler(DatabaseHandler):
    # def upsert_order(self, order: Order):
    #     existing = self.query(
    #         "SELECT id FROM Orders WHERE store_id = (SELECT id FROM Stores WHERE store_name = ?) AND vendor_id = (SELECT id FROM Vendors WHERE name = ?) AND date = ?",
    #         (order.store, order.vendor, order.date),
    #         fetchone=True
    #     )

    #     if existing:
    #         self.execute("DELETE FROM OrderItems WHERE order_id = ?", (existing["id"],))
    #         self.execute("DELETE FROM Orders WHERE id = ?", (existing["id"],))

    #     order_id = self.execute(
    #         "INSERT INTO Orders (store_id, vendor_id, date) VALUES ((SELECT id FROM Stores WHERE store_name = ?), (SELECT id FROM Vendors WHERE name = ?), ?)",
    #         (order.store, order.vendor, order.date),
    #         commit=True,
    #         return_lastrowid=True
    #     )

    #     for item in order.items:
    #         item_id = self.get_item_id_by_name(item.name)
    #         if item_id:
    #             self.execute(
    #                 "INSERT INTO OrderItems (order_id, item_id, quantity, cost_per) VALUES (?, ?, ?, ?)",
    #                 (order_id, item_id, item.quantity, item.cost_per),
    #                 commit=True
    #             )

    # def get_item_id_by_name(self, name: str):
    #     result = self.query("SELECT id FROM Items WHERE name = ?", (name,), fetchone=True)
    #     return result["id"] if result else None

    def get_all_orders_summary(self, limit: int = 100) -> list[dict]:
        query = """
            SELECT o.id, s.store_name, v.name, o.date,
                   COUNT(oi.id) AS item_count,
                   SUM(oi.quantity * oi.cost_per) AS total_cost,
                   o.placed
            FROM Orders o
            JOIN Stores s ON o.store_id = s.id
            JOIN Vendors v ON o.vendor_id = v.id
            LEFT JOIN OrderItems oi ON oi.order_id = o.id
            GROUP BY o.id
            ORDER BY o.date DESC
            LIMIT ?
        """

        def row_to_dict(row):
            return {
                "id":          row[0],
                "store_name":  row[1],
                "vendor_name": row[2],
                "date":        row[3],
                "item_count":  row[4],
                "total_cost":  row[5] or 0,
                "placed":      bool(row[6])
            }

        return self.fetch_all(query, (limit,), transform=row_to_dict)
    
    def get_order_summary_by_id(self, order_id: int) -> dict | None:
        query = """
            SELECT o.id, o.date, o.placed, s.store_name, v.name AS vendor_name,
                   SUM(oi.quantity * oi.cost_per) AS total_cost
            FROM Orders o
            JOIN Stores s ON o.store_id = s.id
            JOIN Vendors v ON o.vendor_id = v.id
            JOIN OrderItems oi ON oi.order_id = o.id
            WHERE o.id = ?
        """
        return self.fetch_one(query, (order_id,))

    def get_order_items(self, order_id: int) -> list[dict]:
        query = """
            SELECT i.item_name AS name, oi.quantity, oi.cost_per
            FROM OrderItems oi
            JOIN Items i ON oi.item_id = i.id
            WHERE oi.order_id = ?
        """
        return self.fetch_all(query, (order_id,))
    
    def create_order(self, store_id: int, vendor_id: int, date: str) -> int:
        query = """
            INSERT INTO Orders (store_id, vendor_id, date)
            VALUES (?, ?, ?)
        """
        return self.execute(query, (store_id, vendor_id, date))

    def add_order_items(self, order_id: int, items: list[dict]) -> None:
        query = """
            INSERT INTO OrderItems (order_id, item_id, quantity, cost_per)
            VALUES (?, ?, ?, ?)
        """
        params = [(order_id, item["item_id"], item["quantity"], item["cost_per"]) for item in items]
        self.execute_many(query, params)

    def update_order_item(self, order_id: int, item_id: int, quantity: float, cost_per: float) -> None:
        query = """
            UPDATE OrderItems
            SET quantity = ?, cost_per = ?
            WHERE order_id = ? AND item_id = ?
        """
        self.execute(query, (quantity, cost_per, order_id, item_id))

    def delete_order_item(self, order_id: int, item_id: int) -> None:
        query = """
            DELETE FROM OrderItems
            WHERE order_id = ? AND item_id = ?
        """
        self.execute(query, (order_id, item_id))