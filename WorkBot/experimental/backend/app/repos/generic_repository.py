from __future__ import annotations
from typing import Generic, TypeVar, Optional

from backend.repos.ports_generic_repo import RecordStore, Mapper

T = TypeVar("T")

class GenericRepository(Generic[T]):
    """
    A tiny generic repository that delegates the domain-specific bits
    to a Mapper[T] and the DB execution to a RecordStore.

    Typical usage:
        store  = SQLiteStore(DB_PATH)
        mapper = OrderMapper(store)
        repo   = GenericRepository[Order](store, mapper)
        repo.save(order)  # returns id
        repo.find_by_id(42)
    """
    def __init__(self, store: RecordStore, mapper: Mapper[T]):
        self.store = store
        self.mapper = mapper
        # Ensure tables exist once at construction
        self.mapper.ensure_schema()

    # Commands
    def save(self, obj: T) -> int:
        # mapper handles all INSERTs (including any child tables)
        return self.mapper.insert(obj)

    # Queries (opt-in; only if your mapper supports it)
    def find_by_id(self, obj_id: int) -> Optional[T]:
        sql = self.mapper.select_by_id_sql()
        row = self.store.query_one(sql, (obj_id,))
        if row is None:
            return None
        return self.mapper.row_to_obj(row)
