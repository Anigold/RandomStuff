import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE Orders ADD COLUMN placed INTEGER DEFAULT 0")
conn.commit()
conn.close()
