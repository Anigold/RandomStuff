# backend/storage/database_handler.py

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, Optional

from config.paths import DATABASE_PATH

class DatabaseHandler:
    """Base class for SQLite database interactions."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables dict-style access
        return conn

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[dict]:
        with self.get_cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
        
    def fetch_all(self, query: str, params: tuple = (), transform: Optional[callable] = None) -> list[dict]:
        with self.get_cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [transform(row) for row in rows] if transform else [dict(row) for row in rows]
            

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.lastrowid

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self.get_cursor() as cur:
            cur.executemany(query, params_list)
