from __future__ import annotations

from workbot_core.domain.models.item import Item
from workbot_core.infrastructure.database.records.item_record import ItemRecord


def item_record_to_domain(record: ItemRecord) -> Item:
    return Item(
        id=record.id,
        name=record.name,
        category=record.category,
        subcategory=record.subcategory,
        count_unit_quantity=record.count_unit_quantity,
        count_unit_measure=(
            record.count_unit_measure
            or getattr(record, "count_unit", None)
        ),
        custom_each_name=record.custom_each_name,
        each_quantity=record.each_quantity,
        each_measure=record.each_measure,
        weight_quantity=record.weight_quantity,
        weight_measure=record.weight_measure,
        volume_quantity=record.volume_quantity,
        volume_measure=record.volume_measure,
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def item_to_record(item: Item) -> ItemRecord:
    record = ItemRecord(
        id=item.id,
        name=item.name,
        category=item.category,
        subcategory=item.subcategory,
        count_unit_quantity=item.count_unit_quantity,
        count_unit_measure=item.count_unit_measure,
        custom_each_name=item.custom_each_name,
        each_quantity=item.each_quantity,
        each_measure=item.each_measure,
        weight_quantity=item.weight_quantity,
        weight_measure=item.weight_measure,
        volume_quantity=item.volume_quantity,
        volume_measure=item.volume_measure,
        is_active=item.is_active,
    )

    if hasattr(record, "count_unit"):
        record.count_unit = item.count_unit_measure

    return record


def update_item_record(record: ItemRecord, item: Item) -> None:
    record.name = item.name
    record.category = item.category
    record.subcategory = item.subcategory

    record.count_unit_quantity = item.count_unit_quantity
    record.count_unit_measure = item.count_unit_measure

    if hasattr(record, "count_unit"):
        record.count_unit = item.count_unit_measure

    record.custom_each_name = item.custom_each_name

    record.each_quantity = item.each_quantity
    record.each_measure = item.each_measure

    record.weight_quantity = item.weight_quantity
    record.weight_measure = item.weight_measure

    record.volume_quantity = item.volume_quantity
    record.volume_measure = item.volume_measure

    record.is_active = item.is_active