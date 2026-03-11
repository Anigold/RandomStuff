import sqlite3

def clear_all_data(db_path="inventory.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")  # Prevent FK errors while deleting

    tables = [
        "OrderItems",
        "Orders",
        "StoreEmployees",
        "StoreItems",
        "VendorItems",
        "Employees",
        "Positions",
        "Units",
        "Items",
        "Stores",
        "Vendors"
    ]

    for table in tables:
        print(f"Clearing table: {table}")
        cursor.execute(f"DELETE FROM {table};")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")  # Reset autoincrement

    conn.commit()
    conn.close()
    print("All data cleared from the database.")

if __name__ == "__main__":
    clear_all_data()
