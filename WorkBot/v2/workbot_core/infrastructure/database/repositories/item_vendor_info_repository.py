from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.infrastructure.database.mappers.item_vendor_info_mapper import (
    item_vendor_info_record_to_domain,
    item_vendor_info_to_record,
    update_item_vendor_info_record,
)
from workbot_core.infrastructure.database.records.item_vendor_info_record import (
    ItemVendorInfoRecord,
)
from workbot_core.infrastructure.database.repositories.base_repository import SqlRepository


class SqlItemVendorInfoRepository(
    SqlRepository[ItemVendorInfoRecord, ItemVendorInfo]
):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=ItemVendorInfoRecord,
            to_domain=item_vendor_info_record_to_domain,
            to_record=item_vendor_info_to_record,
            update_record=update_item_vendor_info_record,
        )

    def save(self, info: ItemVendorInfo) -> None:
        super().save(info, info.id)

    def get_by_item_vendor_sku(
        self,
        *,
        item_id: str,
        vendor_id: str,
        vendor_sku: str | None,
    ) -> ItemVendorInfo | None:
        statement = select(ItemVendorInfoRecord).where(
            ItemVendorInfoRecord.item_id == item_id,
            ItemVendorInfoRecord.vendor_id == vendor_id,
            ItemVendorInfoRecord.vendor_sku == vendor_sku,
        )

        return self._one_or_none(statement)

    def list_for_item(self, item_id: str) -> list[ItemVendorInfo]:
        statement = select(ItemVendorInfoRecord).where(
            ItemVendorInfoRecord.item_id == item_id
        )
        return self._list(statement)

    def list_for_vendor(self, vendor_id: str) -> list[ItemVendorInfo]:
        statement = select(ItemVendorInfoRecord).where(
            ItemVendorInfoRecord.vendor_id == vendor_id
        )
        return self._list(statement)

    def list_active_for_vendor(self, vendor_id: str) -> list[ItemVendorInfo]:
        statement = select(ItemVendorInfoRecord).where(
            ItemVendorInfoRecord.vendor_id == vendor_id,
            ItemVendorInfoRecord.is_active.is_(True),
        )
        return self._list(statement)