from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.infrastructure.database.mappers.item_store_info_mapper import (
    item_store_info_record_to_domain,
    item_store_info_to_record,
    update_item_store_info_record,
)
from workbot_core.infrastructure.database.records.item_store_info_record import (
    ItemStoreInfoRecord,
)
from workbot_core.infrastructure.database.repositories.base_repository import SqlRepository


class SqlItemStoreInfoRepository(SqlRepository[ItemStoreInfoRecord, ItemStoreInfo]):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=ItemStoreInfoRecord,
            to_domain=item_store_info_record_to_domain,
            to_record=item_store_info_to_record,
            update_record=update_item_store_info_record,
        )

    def save(self, info: ItemStoreInfo) -> None:
        super().save(info, info.id)

    def get_by_item_store(
        self,
        *,
        item_id: str,
        store_id: str,
    ) -> ItemStoreInfo | None:
        statement = select(ItemStoreInfoRecord).where(
            ItemStoreInfoRecord.item_id == item_id,
            ItemStoreInfoRecord.store_id == store_id,
        )

        return self._one_or_none(statement)

    def list_for_item(self, item_id: str) -> list[ItemStoreInfo]:
        statement = select(ItemStoreInfoRecord).where(
            ItemStoreInfoRecord.item_id == item_id
        )
        return self._list(statement)

    def list_for_store(self, store_id: str) -> list[ItemStoreInfo]:
        statement = select(ItemStoreInfoRecord).where(
            ItemStoreInfoRecord.store_id == store_id
        )
        return self._list(statement)