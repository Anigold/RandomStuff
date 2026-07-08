from __future__ import annotations

from workbot_core.domain.models.inventory import (
    InventoryCount,
    InventoryCountLine,
    InventoryCountStatus,
)
from workbot_core.infrastructure.database.records.inventory_record import (
    InventoryCountLineRecord,
    InventoryCountRecord,
)


def inventory_count_record_to_domain(record: InventoryCountRecord) -> InventoryCount:
    return InventoryCount(
        id=record.id,
        store_id=record.store_id,
        count_date=record.count_date,
        status=InventoryCountStatus(record.status),
        notes=record.notes,
        lines=tuple(
            inventory_count_line_record_to_domain(line)
            for line in record.lines
        ),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def inventory_count_to_record(count: InventoryCount) -> InventoryCountRecord:
    return InventoryCountRecord(
        id=count.id,
        store_id=count.store_id,
        count_date=count.count_date,
        status=count.status.value,
        notes=count.notes,
        created_at=count.created_at,
        updated_at=count.updated_at,
        lines=[
            inventory_count_line_to_record(line)
            for line in count.lines
        ],
    )


def update_inventory_count_record(
    record: InventoryCountRecord,
    count: InventoryCount,
) -> None:
    record.store_id = count.store_id
    record.count_date = count.count_date
    record.status = count.status.value
    record.notes = count.notes

    record.lines.clear()
    record.lines.extend(
        inventory_count_line_to_record(line)
        for line in count.lines
    )


def inventory_count_line_record_to_domain(
    record: InventoryCountLineRecord,
) -> InventoryCountLine:
    return InventoryCountLine(
        id=record.id,
        inventory_count_id=record.inventory_count_id,
        item_id=record.item_id,
        quantity=record.quantity,
        unit=record.unit,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def inventory_count_line_to_record(
    line: InventoryCountLine,
) -> InventoryCountLineRecord:
    return InventoryCountLineRecord(
        id=line.id,
        inventory_count_id=line.inventory_count_id,
        item_id=line.item_id,
        quantity=line.quantity,
        unit=line.unit,
        notes=line.notes,
        created_at=line.created_at,
        updated_at=line.updated_at,
    )