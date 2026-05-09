from __future__ import annotations

from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.records.store_record import StoreRecord


def store_record_to_domain(record: StoreRecord) -> Store:
    return Store(
        id=record.id,
        name=record.name,
        is_active=record.is_active,
    )


def store_to_record(store: Store) -> StoreRecord:
    return StoreRecord(
        id=store.id,
        name=store.name,
        is_active=store.is_active,
    )


def update_store_record(record: StoreRecord, store: Store) -> None:
    record.name = store.name
    record.is_active = store.is_active