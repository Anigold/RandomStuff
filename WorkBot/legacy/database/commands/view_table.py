import sqlite3
import pandas as pd

def view_table(table_name, db_path="inventory.db", limit=100):
    conn = sqlite3.connect(db_path)

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit};", conn)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python view_table.py <table_name>")
    else:
        view_table(sys.argv[1])
