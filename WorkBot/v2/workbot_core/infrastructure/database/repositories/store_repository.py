from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.mappers.store_mapper import (
    store_record_to_domain,
    store_to_record,
    update_store_record,
)
from workbot_core.infrastructure.database.records.store_record import StoreRecord
from workbot_core.infrastructure.database.repositories.base_repository import SqlRepository


class SqlStoreRepository(SqlRepository[StoreRecord, Store]):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=StoreRecord,
            to_domain=store_record_to_domain,
            to_record=store_to_record,
            update_record=update_store_record,
        )

    def save(self, store: Store) -> None:
        super().save(store, store.id)

    def get_by_name(self, name: str) -> Store | None:
        statement = select(StoreRecord).where(StoreRecord.name == name)
        return self._one_or_none(statement)

    def list_active(self) -> list[Store]:
        statement = select(StoreRecord).where(StoreRecord.is_active.is_(True))
        return self._list(statement)