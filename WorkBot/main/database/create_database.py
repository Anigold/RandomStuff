
import sqlite3

def create_inventory_schema(db_path: str = "inventory.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS Stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name VARCHAR(64) NOT NULL,
            address BLOB NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(128) NOT NULL,
            position VARCHAR(64) NOT NULL,
            phone_number VARCHAR(11) NOT NULL,
            email VARCHAR(64)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(24) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS StoreEmployees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            store_id INTEGER NOT NULL,
            position_id INTEGER NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES Employees(id),
            FOREIGN KEY (store_id) REFERENCES Stores(id),
            FOREIGN KEY (position_id) REFERENCES Positions(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            minimum_order_cost INTEGER NOT NULL,
            minimum_order_cases INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (store_id) REFERENCES Stores(id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name VARCHAR(128) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS OrderItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            cost_per INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (order_id) REFERENCES Orders(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            units_name VARCHAR NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS VendorItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            vendor_sku VARCHAR NOT NULL,
            price INTEGER NOT NULL,
            units_id VARCHAR,
            case_size INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(id),
            FOREIGN KEY (units_id) REFERENCES Units(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS StoreItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            on_hand INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            store_id INTEGER,
            par INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (store_id) REFERENCES Stores(id)
        )
        """
    ]

    for stmt in schema_statements:
        cur.execute(stmt)

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    create_inventory_schema()