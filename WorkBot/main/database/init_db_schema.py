import sqlite3

def initialize_database(db_path="inventory.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    schema = [
        # Stores
        '''
        CREATE TABLE IF NOT EXISTS Stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT NOT NULL,
            address TEXT NOT NULL
        );
        ''',

        # Employees
        '''
        CREATE TABLE IF NOT EXISTS Employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT
        );
        ''',

        # Positions
        '''
        CREATE TABLE IF NOT EXISTS Positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        ''',

        # StoreEmployees
        '''
        CREATE TABLE IF NOT EXISTS StoreEmployees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            store_id INTEGER NOT NULL,
            position_id INTEGER NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES Employees(id),
            FOREIGN KEY (store_id) REFERENCES Stores(id),
            FOREIGN KEY (position_id) REFERENCES Positions(id)
        );
        ''',

        # Vendors
        '''
        CREATE TABLE IF NOT EXISTS Vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            minimum_order_cost INTEGER NOT NULL,
            minimum_order_cases INTEGER NOT NULL
        );
        ''',

        # Items
        '''
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL
        );
        ''',

        # Orders
        '''
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (store_id) REFERENCES Stores(id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(id)
        );
        ''',

        # OrderItems
        '''
        CREATE TABLE IF NOT EXISTS OrderItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            cost_per INTEGER NOT NULL,  -- in cents
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (order_id) REFERENCES Orders(id)
        );
        ''',

        # Units
        '''
        CREATE TABLE IF NOT EXISTS Units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            units_name TEXT NOT NULL
        );
        ''',

        # VendorItems
        '''
        CREATE TABLE IF NOT EXISTS VendorItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            vendor_id INTEGER NOT NULL,
            vendor_sku TEXT NOT NULL,
            price INTEGER NOT NULL,  -- in cents
            units_id INTEGER,
            case_size INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (vendor_id) REFERENCES Vendors(id),
            FOREIGN KEY (units_id) REFERENCES Units(id)
        );
        ''',

        # StoreItems
        '''
        CREATE TABLE IF NOT EXISTS StoreItems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            on_hand INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            store_id INTEGER,
            par INTEGER NOT NULL,
            FOREIGN KEY (item_id) REFERENCES Items(id),
            FOREIGN KEY (store_id) REFERENCES Stores(id)
        );
        '''
    ]

    for statement in schema:
        cursor.execute(statement)

    conn.commit()
    conn.close()
    print(f"SQLite database initialized at '{db_path}'.")

if __name__ == "__main__":
    initialize_database()
