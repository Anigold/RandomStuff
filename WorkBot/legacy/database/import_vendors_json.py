# import_vendors_json.py

import json
import sqlite3
from pathlib import Path
# from ..config.paths import VENDORS_DIR

DB_PATH = Path(__file__).resolve().parent / "inventory.db"
VENDOR_JSON_PATH = Path(__file__).resolve().parents[1] / 'backend' / 'vendors' / 'vendors.json'

with open(VENDOR_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

count = 0
for name, info in data["vendors"].items():
    # Check if vendor already exists
    cursor.execute("SELECT id FROM Vendors WHERE name = ?", (name,))
    if cursor.fetchone():
        continue

    cursor.execute("""
        INSERT INTO Vendors (name, minimum_order_cost, minimum_order_cases)
        VALUES (?, ?, ?)
    """, (
        name,
        info.get("min_order_value", 0),
        info.get("min_order_cases", 0)
    ))
    count += 1

conn.commit()
conn.close()

print(f"✅ Imported {count} new vendors.")
