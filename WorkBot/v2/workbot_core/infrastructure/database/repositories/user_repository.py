from __future__ import annotations

from sqlalchemy.orm import Session

from workbot_core.domain.models.user import User, UserStoreAccess
from workbot_core.infrastructure.database.mappers.user_mapper import (
    update_user_record,
    user_record_to_domain,
    user_store_access_record_to_domain,
    user_store_access_to_record,
    user_to_record,
)
from workbot_core.infrastructure.database.records.user_record import (
    UserRecord,
    UserStoreAccessRecord,
)


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: str) -> User | None:
        record = self._session.get(UserRecord, user_id)

        if record is None:
            return None

        return user_record_to_domain(record)

    def get_by_username(self, username: str) -> User | None:
        record = (
            self._session.query(UserRecord)
            .filter(UserRecord.username == username)
            .one_or_none()
        )

        if record is None:
            return None

        return user_record_to_domain(record)

    def list_all(self) -> list[User]:
        return [
            user_record_to_domain(record)
            for record in self._session.query(UserRecord).all()
        ]

    def save(self, user: User) -> None:
        record = self._session.get(UserRecord, user.id)

        if record is None:
            self._session.add(user_to_record(user))
            return

        update_user_record(record, user)


class SqlUserStoreAccessRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_user(self, user_id: str) -> list[UserStoreAccess]:
        records = (
            self._session.query(UserStoreAccessRecord)
            .filter(UserStoreAccessRecord.user_id == user_id)
            .all()
        )

        return [
            user_store_access_record_to_domain(record)
            for record in records
        ]

    def list_store_ids_for_user(self, user_id: str) -> list[str]:
        return [
            access.store_id
            for access in self.list_for_user(user_id)
        ]

    def user_has_store_access(self, *, user_id: str, store_id: str) -> bool:
        record = (
            self._session.query(UserStoreAccessRecord)
            .filter(UserStoreAccessRecord.user_id == user_id)
            .filter(UserStoreAccessRecord.store_id == store_id)
            .one_or_none()
        )

        return record is not None

    def save(self, access: UserStoreAccess) -> None:
        existing = (
            self._session.query(UserStoreAccessRecord)
            .filter(UserStoreAccessRecord.user_id == access.user_id)
            .filter(UserStoreAccessRecord.store_id == access.store_id)
            .one_or_none()
        )

        if existing is not None:
            return

        self._session.add(user_store_access_to_record(access))

    def delete_for_user(self, user_id: str) -> None:
        records = (
            self._session.query(UserStoreAccessRecord)
            .filter(UserStoreAccessRecord.user_id == user_id)
            .all()
        )

        for record in records:
            self._session.delete(record)