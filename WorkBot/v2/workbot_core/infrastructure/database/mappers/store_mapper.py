from __future__ import annotations

from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.records.store_record import StoreRecord


def store_record_to_domain(record: StoreRecord) -> Store:
    return Store(
        id=record.id,
        name=record.name,
        is_active=record.is_active,
        general_manager=record.general_manager,
        inventory_clerk=record.inventory_clerk,
        address=record.address,
        phone_number=record.phone_number,
        special_notes=record.special_notes or "",
    )


def store_to_record(store: Store) -> StoreRecord:
    return StoreRecord(
        id=store.id,
        name=store.name,
        is_active=store.is_active,
        general_manager=store.general_manager,
        inventory_clerk=store.inventory_clerk,
        address=store.address,
        phone_number=store.phone_number,
        special_notes=store.special_notes,
    )


def update_store_record(record: StoreRecord, store: Store) -> None:
    record.name = store.name
    record.is_active = store.is_active
    record.general_manager = store.general_manager
    record.inventory_clerk = store.inventory_clerk
    record.address = store.address
    record.phone_number = store.phone_number
    record.special_notes = store.special_notes