from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Iterable, Sequence, Generic, TypeVar, Optional, ContextManager, Any

T = TypeVar("T")

# ---------- Low-level DB contract ----------

class RecordStore(Protocol):
    """
    Minimal DB API the generic repository needs.
    Implemented by concrete stores (e.g., SQLiteStore, PostgresStore).
    """
    def execute(self, sql: str, params: Sequence[Any] | None = None) -> int: ...
    def executemany(self, sql: str, seq_params: Iterable[Sequence[Any]]) -> None: ...
    def query_one(self, sql: str, params: Sequence[Any] | None = None) -> Optional[tuple]: ...
    def query_all(self, sql: str, params: Sequence[Any] | None = None) -> list[tuple]: ...
    def tx(self) -> ContextManager[None]: ...
    def close(self) -> None: ...

@dataclass(frozen=True)
class TableSpec:
    name: str
    create_sql: str

# ---------- Mapper contract (domain plugin) ----------

class Mapper(Protocol, Generic[T]):
    """
    Domain plug-in that knows:
      - how to create schema
      - how to INSERT objects
      - how to SELECT by id (SQL string)
      - how to convert DB rows back to objects
    """
    def ensure_schema(self) -> None: ...
    def insert(self, obj: T) -> int: ...
    def select_by_id_sql(self) -> str: ...
    def row_to_obj(self, row: Sequence[Any]) -> T: ...
