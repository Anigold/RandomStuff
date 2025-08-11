from __future__ import annotations
from typing import Optional
from .database_handler import DatabaseHandler
from backend.models.order import Order

class OrderDatabaseHandler(DatabaseHandler):
    def get_all_orders_summary(self, limit: int = 100, offset: int = 0) -> list[dict]:
        query = '''
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
        '''
        return self.fetch_all(query, (limit, offset))

    def get_order_summary_by_id(self, order_id: int) -> Optional[dict]:
        query = '''
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
        '''
        return self.fetch_one(query, (order_id,))

    def get_order_items(self, order_id: int) -> list[dict]:
        query = '''
            SELECT
                i.id         AS item_id,
                i.item_name  AS name,
                oi.quantity  AS quantity,
                oi.cost_per  AS cost_per
            FROM OrderItems oi
            JOIN Items i ON i.id = oi.item_id
            WHERE oi.order_id = ?
            ORDER BY i.item_name ASC
        '''
        return self.fetch_all(query, (order_id,))

    def save_order(self, order: Order) -> int:
        '''
        Insert or update an order and its items, ensuring related entities exist.
        Returns the order_id.
        '''
        # Ensure store
        store_row = self.fetch_one(
            'SELECT id FROM Stores WHERE store_name = ?', (order.store,)
        )
        if not store_row:
            store_id = self.execute(
                'INSERT INTO Stores (store_name, address) VALUES (?, ?)',
                (order.store, b'')
            )
        else:
            store_id = store_row['id']

        # Ensure vendor
        vendor_row = self.fetch_one(
            'SELECT id FROM Vendors WHERE name = ?', (order.vendor,)
        )
        if not vendor_row:
            vendor_id = self.execute(
                'INSERT INTO Vendors (name, minimum_order_cost, minimum_order_cases) VALUES (?, ?, ?)',
                (order.vendor, 0, 0)
            )
        else:
            vendor_id = vendor_row['id']

        # Upsert order
        order_id = self.upsert_order(store_id, vendor_id, order.date)

        # Prepare items
        items_payload = []
        for item in order.items:
            item_row = self.fetch_one(
                'SELECT id FROM Items WHERE item_name = ?', (item.name,)
            )
            if not item_row:
                item_id = self.execute(
                    'INSERT INTO Items (item_name) VALUES (?)', (item.name,)
                )
            else:
                item_id = item_row['id']

            items_payload.append({
                'item_id': item_id,
                'quantity': float(item.quantity),
                'cost_per': float(getattr(item, 'cost_per', 0.0))
            })

        # Replace existing items
        self.replace_order_items(order_id, items_payload)

        return order_id
    
    def create_order(self, store_id: int, vendor_id: int, date: str) -> int:
        # Unique on (store_id, vendor_id, date)? If so, this will raise on dup (which is good).
        query = 'INSERT INTO Orders (store_id, vendor_id, date) VALUES (?, ?, ?)'
        return self.execute(query, (store_id, vendor_id, date))  # lastrowid

    def add_order_items(self, order_id: int, items: list[dict]) -> None:
        # items: [{'item_id': int, 'quantity': float, 'cost_per': float}, ...]
        query = 'INSERT INTO OrderItems (order_id, item_id, quantity, cost_per) VALUES (?, ?, ?, ?)'
        params = [(order_id, it['item_id'], it['quantity'], it['cost_per']) for it in items]
        self.execute_many(query, params)

    def update_order_item(self, order_id: int, item_id: int, quantity: float, cost_per: float) -> None:
        query = 'UPDATE OrderItems SET quantity = ?, cost_per = ? WHERE order_id = ? AND item_id = ?'
        self.execute(query, (quantity, cost_per, order_id, item_id))

    def delete_order_item(self, order_id: int, item_id: int) -> None:
        query = 'DELETE FROM OrderItems WHERE order_id = ? AND item_id = ?'
        self.execute(query, (order_id, item_id))

    def upsert_order(self, store_id: int, vendor_id: int, date: str) -> int:
        '''
        Insert an order if not present, otherwise return existing id.
        '''
        row = self.fetch_one(
            'SELECT id FROM Orders WHERE store_id = ? AND vendor_id = ? AND date = ?',
            (store_id, vendor_id, date)
        )
        if row:
            return row['id']

        return self.execute(
            'INSERT INTO Orders (store_id, vendor_id, date) VALUES (?, ?, ?)',
            (store_id, vendor_id, date)
        )

    def replace_order_items(self, order_id: int, items: list[dict]) -> None:
        '''Delete existing items and insert the new set.'''
        self.execute('DELETE FROM OrderItems WHERE order_id = ?', (order_id,))
        if items:
            self.execute_many(
                'INSERT INTO OrderItems (order_id, item_id, quantity, cost_per) VALUES (?, ?, ?, ?)',
                [(order_id, it['item_id'], it['quantity'], it['cost_per']) for it in items]
            )
