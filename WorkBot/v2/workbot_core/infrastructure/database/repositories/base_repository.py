from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.infrastructure.database.base import Base


RecordT = TypeVar("RecordT", bound=Base)
DomainT = TypeVar("DomainT")


class SqlRepository(Generic[RecordT, DomainT]):
    def __init__(
        self,
        session: Session,
        record_type: type[RecordT],
        to_domain: Callable[[RecordT], DomainT],
        to_record: Callable[[DomainT], RecordT],
        update_record: Callable[[RecordT, DomainT], None],
    ) -> None:
        self._session = session
        self._record_type = record_type
        self._to_domain = to_domain
        self._to_record = to_record
        self._update_record = update_record

    def get_by_id(self, record_id: str) -> DomainT | None:
        record = self._session.get(self._record_type, record_id)

        if record is None:
            return None

        return self._to_domain(record)

    def list_all(self) -> list[DomainT]:
        records = self._session.scalars(select(self._record_type)).all()
        return [self._to_domain(record) for record in records]

    def save(self, domain_obj: DomainT, record_id: str) -> None:
        existing = self._session.get(self._record_type, record_id)

        if existing is None:
            self._session.add(self._to_record(domain_obj))
            self._session.flush()
            return

        self._update_record(existing, domain_obj)
        self._session.flush()

    def delete(self, record_id: str) -> None:
        existing = self._session.get(self._record_type, record_id)

        if existing is None:
            return

        self._session.delete(existing)

    def _one_or_none(self, statement: Any) -> DomainT | None:
        record = self._session.scalars(statement).one_or_none()

        if record is None:
            return None

        return self._to_domain(record)

    def _list(self, statement: Any) -> list[DomainT]:
        records: Sequence[RecordT] = self._session.scalars(statement).all()
        return [self._to_domain(record) for record in records]
    
    def exists(self, record_id: str) -> bool:
        return self._session.get(self._record_type, record_id) is not None