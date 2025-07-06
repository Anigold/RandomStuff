import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "inventory.db"

def add_unique_constraint():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if constraint already exists (SQLite doesn't have direct constraint names)
    # So we recreate the table if necessary

    cursor.execute("PRAGMA foreign_keys=off;")
    conn.commit()

    # Rename original table
    cursor.execute("ALTER TABLE Orders RENAME TO Orders_old;")

    # Recreate with UNIQUE constraint
    cursor.execute("""
    CREATE TABLE Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER NOT NULL,
        vendor_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        placed INTEGER DEFAULT 0,
        FOREIGN KEY (store_id) REFERENCES Stores(id),
        FOREIGN KEY (vendor_id) REFERENCES Vendors(id),
        UNIQUE (store_id, vendor_id, date)
    );
    """)

    # Copy data from old table
    cursor.execute("""
    INSERT OR IGNORE INTO Orders (id, store_id, vendor_id, date, placed)
    SELECT id, store_id, vendor_id, date, placed FROM Orders_old;
    """)

    # Drop old table
    cursor.execute("DROP TABLE Orders_old;")
    conn.commit()

    cursor.execute("PRAGMA foreign_keys=on;")
    conn.commit()
    conn.close()
    print("✅ Unique constraint added successfully.")

if __name__ == "__main__":
    add_unique_constraint()
