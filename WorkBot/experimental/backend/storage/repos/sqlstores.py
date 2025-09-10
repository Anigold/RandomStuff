from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Sequence, Optional, Any

from backend.repos.ports_generic_repo import RecordStore

class SQLiteStore(RecordStore):
    """
    Lightweight SQLite RecordStore.
    - Autocommit for read-only
    - Use `with store.tx(): ...` for write batches
    """
    def __init__(self, db_path: Path | str):
        self._path = str(db_path)
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row  # named access if you want

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> int:
        cur = self._conn.execute(sql, params or [])
        self._conn.commit()  # autocommit single statements
        return int(cur.lastrowid or 0)

    def executemany(self, sql: str, seq_params: Iterable[Sequence[Any]]) -> None:
        self._conn.executemany(sql, seq_params)
        self._conn.commit()

    def query_one(self, sql: str, params: Sequence[Any] | None = None) -> Optional[tuple]:
        cur = self._conn.execute(sql, params or [])
        row = cur.fetchone()
        return tuple(row) if row is not None else None

    def query_all(self, sql: str, params: Sequence[Any] | None = None) -> list[tuple]:
        cur = self._conn.execute(sql, params or [])
        rows = cur.fetchall()
        return [tuple(r) for r in rows]

    @contextmanager
    def tx(self):
        try:
            self._conn.execute("BEGIN")
            yield
            self._conn.commit()
        except:
            self._conn.rollback()
            raise

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
