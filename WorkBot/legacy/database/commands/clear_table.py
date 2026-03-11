import sqlite3
import argparse

def clear_table(db_path: str, table_name: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(f'DELETE FROM {table_name};')
        conn.commit()
        print(f"✅ All data deleted from '{table_name}'")
    except sqlite3.Error as e:
        print(f"❌ Error deleting from '{table_name}': {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clear all rows from a specified SQLite table.")
    parser.add_argument("table_name", help="Name of the table to clear")
    parser.add_argument(
        "--db", 
        default="./inventory.db",
        help="Path to the SQLite database (default: main/database/inventory.db)"
    )
    args = parser.parse_args()

    clear_table(args.db, args.table_name)
