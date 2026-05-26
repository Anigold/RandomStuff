from __future__ import annotations

from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.infrastructure.database.records.item_vendor_info_record import (
    ItemVendorInfoRecord,
)


def item_vendor_info_record_to_domain(record: ItemVendorInfoRecord) -> ItemVendorInfo:
    return ItemVendorInfo(
        id=record.id,
        item_id=record.item_id,
        vendor_id=record.vendor_id,
        vendor_sku=record.vendor_sku,
        purchase_unit=record.purchase_unit,
        pack_size=record.pack_size,
        price=record.price,
        last_purchase_date=record.last_purchase_date,
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def item_vendor_info_to_record(info: ItemVendorInfo) -> ItemVendorInfoRecord:
    return ItemVendorInfoRecord(
        id=info.id,
        item_id=info.item_id,
        vendor_id=info.vendor_id,
        vendor_sku=info.vendor_sku,
        purchase_unit=info.purchase_unit,
        pack_size=info.pack_size,
        price=info.price,
        last_purchase_date=info.last_purchase_date,
        is_active=info.is_active,
    )


def update_item_vendor_info_record(
    record: ItemVendorInfoRecord,
    info: ItemVendorInfo,
) -> None:
    record.item_id = info.item_id
    record.vendor_id = info.vendor_id
    record.vendor_sku = info.vendor_sku
    record.purchase_unit = info.purchase_unit
    record.pack_size = info.pack_size
    record.price = info.price
    record.last_purchase_date = info.last_purchase_date
    record.is_active = info.is_active