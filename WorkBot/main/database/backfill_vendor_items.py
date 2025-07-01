import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "inventory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Find all unique (vendor_id, item_id) pairs from existing OrderItems
cursor.execute("""
    SELECT DISTINCT Orders.vendor_id, OrderItems.item_id
    FROM OrderItems
    JOIN Orders ON OrderItems.order_id = Orders.id
""")
vendor_item_pairs = cursor.fetchall()

created = 0
for vendor_id, item_id in vendor_item_pairs:
    # Check if already in VendorItems
    cursor.execute("""
        SELECT 1 FROM VendorItems
        WHERE vendor_id = ? AND item_id = ?
    """, (vendor_id, item_id))
    if cursor.fetchone():
        continue

    # Try to get a recent cost and dummy SKU
    cursor.execute("""
        SELECT cost_per FROM OrderItems
        JOIN Orders ON OrderItems.order_id = Orders.id
        WHERE Orders.vendor_id = ? AND OrderItems.item_id = ?
        ORDER BY Orders.date DESC LIMIT 1
    """, (vendor_id, item_id))
    row = cursor.fetchone()
    price = row[0] if row else 0

    sku = f"SKU-{vendor_id}-{item_id}"  # placeholder
    cursor.execute("""
    INSERT INTO VendorItems (vendor_id, item_id, vendor_sku, price, case_size)
    VALUES (?, ?, ?, ?, ?)
""", (vendor_id, item_id, sku, price, 1))

    created += 1

conn.commit()
conn.close()
print(f"✅ Backfilled {created} VendorItems.")
