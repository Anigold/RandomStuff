import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

def normalize_name(name):
    return name.strip().lower()

def get_or_create(cursor, table, key_field, value, cache, defaults=None):
    value_norm = normalize_name(value)
    if value_norm in cache:
        return cache[value_norm]

    cursor.execute(f"SELECT id FROM {table} WHERE {key_field} = ?", (value,))
    row = cursor.fetchone()
    if row:
        cache[value_norm] = row[0]
        return row[0]

    # Handle special cases
    if table == "Stores":
        address = (defaults or {}).get("address", "UNKNOWN")
        cursor.execute(f"INSERT INTO Stores ({key_field}, address) VALUES (?, ?)", (value, address))

    elif table == "Vendors":
        min_cost = (defaults or {}).get("minimum_order_cost", 0)
        min_cases = (defaults or {}).get("minimum_order_cases", 0)
        cursor.execute(f"""
            INSERT INTO Vendors (name, minimum_order_cost, minimum_order_cases)
            VALUES (?, ?, ?)
        """, (value, min_cost, min_cases))

    else:
        cursor.execute(f"INSERT INTO {table} ({key_field}) VALUES (?)", (value,))

    id_ = cursor.lastrowid
    cache[value_norm] = id_
    return id_



def import_purchase_log(xlsx_path, db_path="inventory.db"):
    df = pd.read_excel(xlsx_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Caches for fast lookup
    vendor_cache = {}
    store_cache = {}
    item_cache = {}
    order_cache = {}  # key: (store_id, vendor_id, date) → order_id

    # OPTIONAL: Prepopulate stores (if not in sheet) or set a default
    def guess_store_from_invoice(store_name):
        name = store_name.split(' - ')[1]
        if "College Ave".upper() in name.upper():
            return "Collegetown"
        if "Meadow".upper() in name.upper():
            return "Bakery"
        if "Trip".upper() in name.upper():
            return "Triphammer"
        if "State".upper() in name.upper():
            return "Downtown"
        if "East".upper() in name.upper():
            return "Easthill"
        if 'Syracue'.upper() in name.upper():
            return 'Syracuse'
        return "Unspecified Store"

    df.columns = [col.strip().upper() for col in df.columns]
    for _, row in df.iterrows():
        store_name   = str(row['STORE'])
        vendor_name  = str(row['VENDOR'])
        item_name    = str(row['ITEM'])
        quantity     = int(row['QUANTITY'])
        amount       = float(row['AMOUNT'])   # total amount
        unit_price   = float(row['CU PRICE']) # price per unit
        received_raw = row['RECEIVED DATE']
        invoice      = str(row['INVOICE NO'])

        # Parse/store date
        received_date = (
            received_raw.date() if isinstance(received_raw, datetime)
            else datetime.strptime(str(received_raw), "%m/%d/%Y").date()
        )

        # Guess store name based on invoice
        store_name_guess = guess_store_from_invoice(store_name)

        # --- insert/get IDs ---
        store_id = get_or_create(cursor, "Stores", "store_name", store_name_guess, store_cache, defaults={"address": "UNKNOWN"})
        vendor_id = get_or_create(cursor, "Vendors", "name", vendor_name, vendor_cache,
                          defaults={"minimum_order_cost": 0, "minimum_order_cases": 0})
        item_id   = get_or_create(cursor, "Items",   "item_name",  item_name,   item_cache)

        order_key = (store_id, vendor_id, received_date)
        if order_key not in order_cache:
            cursor.execute(
                "INSERT INTO Orders (store_id, vendor_id, date) VALUES (?, ?, ?)",
                (store_id, vendor_id, received_date)
            )
            order_id = cursor.lastrowid
            order_cache[order_key] = order_id
        else:
            order_id = order_cache[order_key]

        # --- insert order item ---
        cursor.execute(
            "INSERT INTO OrderItems (item_id, order_id, quantity, cost_per) VALUES (?, ?, ?, ?)",
            (item_id, order_id, quantity, int(round(unit_price * 100)))  # convert to cents
        )

    conn.commit()
    conn.close()
    print("Purchase log imported successfully.")

if __name__ == "__main__":
    import_purchase_log("purchase_log.xlsx")  # Update with your actual filename
