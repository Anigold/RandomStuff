from __future__ import annotations

from workbot_core.domain.models.item import Item
from workbot_core.infrastructure.database.records.item_record import ItemRecord


def item_record_to_domain(record: ItemRecord) -> Item:
    return Item(
        id=record.id,
        name=record.name,
        category=record.category,
        subcategory=record.subcategory,
        count_unit=record.count_unit,
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def item_to_record(item: Item) -> ItemRecord:
    return ItemRecord(
        id=item.id,
        name=item.name,
        category=item.category,
        subcategory=item.subcategory,
        count_unit=item.count_unit,
        is_active=item.is_active,
    )


def update_item_record(record: ItemRecord, item: Item) -> None:
    record.name = item.name
    record.category = item.category
    record.subcategory = item.subcategory
    record.count_unit = item.count_unit
    record.is_active = item.is_active