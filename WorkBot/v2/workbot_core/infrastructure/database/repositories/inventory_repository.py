from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from workbot_core.domain.models.inventory import InventoryCount
from workbot_core.infrastructure.database.mappers.inventory_mapper import (
    inventory_count_record_to_domain,
    inventory_count_to_record,
    update_inventory_count_record,
)
from workbot_core.infrastructure.database.records.inventory_record import (
    InventoryCountRecord,
)
from workbot_core.infrastructure.database.repositories.base_repository import (
    SqlRepository,
)


class SqlInventoryCountRepository(
    SqlRepository[InventoryCountRecord, InventoryCount]
):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=InventoryCountRecord,
            to_domain=inventory_count_record_to_domain,
            to_record=inventory_count_to_record,
            update_record=update_inventory_count_record,
        )

    def save(self, count: InventoryCount) -> None:
        super().save(count, count.id)

    def get_by_id(self, count_id: str) -> InventoryCount | None:
        statement = (
            select(InventoryCountRecord)
            .options(selectinload(InventoryCountRecord.lines))
            .where(InventoryCountRecord.id == count_id)
        )

        return self._one_or_none(statement)

    def list_all(self) -> list[InventoryCount]:
        statement = (
            select(InventoryCountRecord)
            .options(selectinload(InventoryCountRecord.lines))
            .order_by(
                InventoryCountRecord.count_date.desc(),
                InventoryCountRecord.created_at.desc(),
                InventoryCountRecord.id.desc(),
            )
        )

        return self._list(statement)

    def list_for_store(self, store_id: str) -> list[InventoryCount]:
        statement = (
            select(InventoryCountRecord)
            .options(selectinload(InventoryCountRecord.lines))
            .where(InventoryCountRecord.store_id == store_id)
            .order_by(
                InventoryCountRecord.count_date.desc(),
                InventoryCountRecord.created_at.desc(),
                InventoryCountRecord.id.desc(),
            )
        )

        return self._list(statement)