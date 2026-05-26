from __future__ import annotations

from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.infrastructure.database.records.item_store_info_record import (
    ItemStoreInfoRecord,
)


def item_store_info_record_to_domain(record: ItemStoreInfoRecord) -> ItemStoreInfo:
    return ItemStoreInfo(
        id=record.id,
        item_id=record.item_id,
        store_id=record.store_id,
        count_unit=record.count_unit,
        par=record.par,
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def item_store_info_to_record(info: ItemStoreInfo) -> ItemStoreInfoRecord:
    return ItemStoreInfoRecord(
        id=info.id,
        item_id=info.item_id,
        store_id=info.store_id,
        count_unit=info.count_unit,
        par=info.par,
        is_active=info.is_active,
    )


def update_item_store_info_record(
    record: ItemStoreInfoRecord,
    info: ItemStoreInfo,
) -> None:
    record.item_id = info.item_id
    record.store_id = info.store_id
    record.count_unit = info.count_unit
    record.par = info.par
    record.is_active = info.is_active