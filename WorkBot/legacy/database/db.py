import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "inventory.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dict-like access: row['id']
    return conn
