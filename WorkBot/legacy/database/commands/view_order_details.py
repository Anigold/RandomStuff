import sqlite3
import pandas as pd

def view_order(order_id, db_path="inventory.db"):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT
        Orders.id            AS order_id,
        Orders.date          AS order_date,
        Stores.store_name    AS store,
        Vendors.name         AS vendor,
        Items.item_name      AS item,
        OrderItems.quantity  AS quantity,
        ROUND(OrderItems.cost_per / 100.0, 2) AS cost_per_unit,
        ROUND((OrderItems.cost_per * OrderItems.quantity) / 100.0, 2) AS line_total
    FROM Orders
    JOIN Stores      ON Orders.store_id = Stores.id
    JOIN Vendors     ON Orders.vendor_id = Vendors.id
    JOIN OrderItems  ON OrderItems.order_id = Orders.id
    JOIN Items       ON OrderItems.item_id = Items.id
    WHERE Orders.id = ?
    """

    df = pd.read_sql_query(query, conn, params=(order_id,))

    if df.empty:
        print(f"No order found with ID {order_id}.")
    else:
        print(f"\n🧾 Order ID: {order_id}")
        print(f"📍 Store:  {df['store'][0]}")
        print(f"🚚 Vendor: {df['vendor'][0]}")
        print(f"📅 Date:   {df['order_date'][0]}")
        print("\n📦 Items:\n")
        print(df[['item', 'quantity', 'cost_per_unit', 'line_total']].to_string(index=False))

        total = df['line_total'].sum()
        print(f"\n💰 Total Order Cost: ${total:.2f}")

    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python view_order_details.py <order_id>")
    else:
        view_order(int(sys.argv[1]))
