from __future__ import annotations

from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from workbot_core.domain.models.order import Order
from workbot_core.infrastructure.database.mappers.order_mapper import (
    order_record_to_domain,
    order_to_record,
    update_order_record,
)
from workbot_core.infrastructure.database.records.order_record import OrderRecord


class SqlOrderRepository:
    
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, order_id: str) -> Order | None:
        statement = (
            select(OrderRecord)
            .options(selectinload(OrderRecord.lines))
            .where(OrderRecord.id == order_id)
        )

        record = self._session.scalars(statement).one_or_none()

        if record is None:
            return None

        return order_record_to_domain(record)

    def get_by_source_reference(
        self,
        *,
        store_id: str,
        vendor_id: str,
        order_date: date,
        source: str,
        source_reference: str,
    ) -> Order | None:
        statement = (
            select(OrderRecord)
            .options(selectinload(OrderRecord.lines))
            .where(
                OrderRecord.store_id == store_id,
                OrderRecord.vendor_id == vendor_id,
                OrderRecord.order_date == order_date,
                OrderRecord.source == source,
                OrderRecord.source_reference == source_reference,
            )
        )

        record = self._session.scalars(statement).one_or_none()

        if record is None:
            return None

        return order_record_to_domain(record)

    def list_all(self) -> list[Order]:
        statement = (
            select(OrderRecord)
            .options(selectinload(OrderRecord.lines))
            .order_by(OrderRecord.order_date.desc())
        )

        records = self._session.scalars(statement).all()

        return [order_record_to_domain(record) for record in records]

    def list_by_store(
        self,
        store_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        statement = select(OrderRecord).where(OrderRecord.store_id == store_id)
        statement = self._apply_date_range(statement, start_date, end_date)

        return self._list(statement)

    def list_by_vendor(
        self,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        statement = select(OrderRecord).where(OrderRecord.vendor_id == vendor_id)
        statement = self._apply_date_range(statement, start_date, end_date)

        return self._list(statement)

    def list_by_store_and_vendor(
        self,
        store_id: str,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        statement = select(OrderRecord).where(
            OrderRecord.store_id == store_id,
            OrderRecord.vendor_id == vendor_id,
        )
        statement = self._apply_date_range(statement, start_date, end_date)

        return self._list(statement)

    def save(self, order: Order) -> None:
        existing = self._session.get(OrderRecord, order.id)

        if existing is None:
            self._session.add(order_to_record(order))
            self._session.flush()
            return

        update_order_record(existing, order)
        self._session.flush()

    def delete(self, order_id: str) -> None:
        existing = self._session.get(OrderRecord, order_id)

        if existing is None:
            return

        self._session.delete(existing)
        self._session.flush()

    def exists(self, order_id: str) -> bool:
        return self._session.get(OrderRecord, order_id) is not None

    def _list(self, statement: Select[tuple[OrderRecord]]) -> list[Order]:
        statement = (
            statement
            .options(selectinload(OrderRecord.lines))
            .order_by(OrderRecord.order_date.desc())
        )

        records = self._session.scalars(statement).all()

        return [order_record_to_domain(record) for record in records]

    @staticmethod
    def _apply_date_range(
        statement: Select[tuple[OrderRecord]],
        start_date: date | None,
        end_date: date | None,
    ) -> Select[tuple[OrderRecord]]:
        if start_date is not None:
            statement = statement.where(OrderRecord.order_date >= start_date)

        if end_date is not None:
            statement = statement.where(OrderRecord.order_date <= end_date)

        return statement