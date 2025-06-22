import sqlite3

conn = sqlite3.connect("inventory.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

print("Tables:", tables)

for table in tables:
    print(f"\n--- {table[0]} ---")
    cur.execute(f"PRAGMA table_info({table[0]});")
    for col in cur.fetchall():
        print(col)

conn.close()
