from __future__ import annotations

from workbot_core.domain.models.order import Order, OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus
from workbot_core.infrastructure.database.records.order_line_record import OrderLineRecord
from workbot_core.infrastructure.database.records.order_record import OrderRecord


def order_line_record_to_domain(record: OrderLineRecord) -> OrderLine:
    return OrderLine(
        id=record.id,
        order_id=record.order_id,
        item_id=record.item_id,
        item_vendor_info_id=record.item_vendor_info_id,
        source_item_name=record.source_item_name,
        source_vendor_sku=record.source_vendor_sku,
        item_name_snapshot=record.item_name_snapshot,
        vendor_sku_snapshot=record.vendor_sku_snapshot,
        unit_price_snapshot=record.unit_price_snapshot,
        quantity=record.quantity,
        unit=record.unit,
        status=OrderLineStatus(record.status),
        status_reason=record.status_reason,
        moved_to_order_id=record.moved_to_order_id,
        notes=record.notes or "",
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def order_line_to_record(line: OrderLine) -> OrderLineRecord:
    return OrderLineRecord(
        id=line.id,
        order_id=line.order_id,
        item_id=line.item_id,
        item_vendor_info_id=line.item_vendor_info_id,
        source_item_name=line.source_item_name,
        source_vendor_sku=line.source_vendor_sku,
        item_name_snapshot=line.item_name_snapshot,
        vendor_sku_snapshot=line.vendor_sku_snapshot,
        unit_price_snapshot=line.unit_price_snapshot,
        quantity=line.quantity,
        unit=line.unit,
        status=line.status.value,
        status_reason=line.status_reason,
        moved_to_order_id=line.moved_to_order_id,
        notes=line.notes or "",
        created_at=line.created_at,
        updated_at=line.updated_at,
    )


def update_order_line_record(record: OrderLineRecord, line: OrderLine) -> None:
    record.item_id = line.item_id
    record.item_vendor_info_id = line.item_vendor_info_id
    record.source_item_name = line.source_item_name
    record.source_vendor_sku = line.source_vendor_sku
    record.item_name_snapshot = line.item_name_snapshot
    record.vendor_sku_snapshot = line.vendor_sku_snapshot
    record.unit_price_snapshot = line.unit_price_snapshot
    record.quantity = line.quantity
    record.unit = line.unit
    record.status = line.status.value
    record.status_reason = line.status_reason
    record.moved_to_order_id = line.moved_to_order_id
    record.notes = line.notes or ""

    if line.created_at is not None:
        record.created_at = line.created_at

    if line.updated_at is not None:
        record.updated_at = line.updated_at


def order_record_to_domain(record: OrderRecord) -> Order:
    return Order(
        id=record.id,
        store_id=record.store_id,
        vendor_id=record.vendor_id,
        order_date=record.order_date,
        delivery_date=record.delivery_date,
        status=OrderStatus(record.status),
        source=record.source,
        source_reference=record.source_reference,
        notes=record.notes or "",
        lines=tuple(order_line_record_to_domain(line) for line in record.lines),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def order_to_record(order: Order) -> OrderRecord:
    return OrderRecord(
        id=order.id,
        store_id=order.store_id,
        vendor_id=order.vendor_id,
        order_date=order.order_date,
        delivery_date=order.delivery_date,
        status=order.status.value,
        source=order.source,
        source_reference=order.source_reference,
        notes=order.notes or "",
        lines=[order_line_to_record(line) for line in order.lines],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def update_order_record(record: OrderRecord, order: Order) -> None:
    record.store_id = order.store_id
    record.vendor_id = order.vendor_id
    record.order_date = order.order_date
    record.delivery_date = order.delivery_date
    record.status = order.status.value
    record.source = order.source
    record.source_reference = order.source_reference
    record.notes = order.notes or ""

    if order.created_at is not None:
        record.created_at = order.created_at

    if order.updated_at is not None:
        record.updated_at = order.updated_at

    existing_lines_by_id = {line.id: line for line in record.lines}
    incoming_line_ids = {line.id for line in order.lines}

    for existing_line in list(record.lines):
        if existing_line.id not in incoming_line_ids:
            record.lines.remove(existing_line)

    for incoming_line in order.lines:
        existing_line = existing_lines_by_id.get(incoming_line.id)

        if existing_line is None:
            record.lines.append(order_line_to_record(incoming_line))
        else:
            update_order_line_record(existing_line, incoming_line)