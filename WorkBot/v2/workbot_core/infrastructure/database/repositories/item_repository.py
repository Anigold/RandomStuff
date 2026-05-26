from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.domain.models.item import Item
from workbot_core.infrastructure.database.mappers.item_mapper import (
    item_record_to_domain,
    item_to_record,
    update_item_record,
)
from workbot_core.infrastructure.database.records.item_record import ItemRecord
from workbot_core.infrastructure.database.repositories.base_repository import SqlRepository


class SqlItemRepository(SqlRepository[ItemRecord, Item]):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=ItemRecord,
            to_domain=item_record_to_domain,
            to_record=item_to_record,
            update_record=update_item_record,
        )

    def save(self, item: Item) -> None:
        super().save(item, item.id)

    def get_by_name(self, name: str) -> Item | None:
        statement = select(ItemRecord).where(ItemRecord.name == name)
        return self._one_or_none(statement)

    def list_active(self) -> list[Item]:
        statement = select(ItemRecord).where(ItemRecord.is_active.is_(True))
        return self._list(statement)