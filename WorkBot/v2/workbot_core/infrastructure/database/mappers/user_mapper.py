from __future__ import annotations

from workbot_core.domain.models.user import User, UserRole, UserStoreAccess
from workbot_core.infrastructure.database.records.user_record import (
    UserRecord,
    UserStoreAccessRecord,
)


def user_record_to_domain(record: UserRecord) -> User:
    return User(
        id=record.id,
        username=record.username,
        password_hash=record.password_hash,
        role=UserRole(record.role),
        is_active=record.is_active,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def user_to_record(user: User) -> UserRecord:
    return UserRecord(
        id=user.id,
        username=user.username,
        password_hash=user.password_hash,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def update_user_record(record: UserRecord, user: User) -> None:
    record.username = user.username
    record.password_hash = user.password_hash
    record.role = user.role.value
    record.is_active = user.is_active

    if user.created_at is not None:
        record.created_at = user.created_at

    if user.updated_at is not None:
        record.updated_at = user.updated_at


def user_store_access_record_to_domain(
    record: UserStoreAccessRecord,
) -> UserStoreAccess:
    return UserStoreAccess(
        id=record.id,
        user_id=record.user_id,
        store_id=record.store_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def user_store_access_to_record(
    access: UserStoreAccess,
) -> UserStoreAccessRecord:
    return UserStoreAccessRecord(
        id=access.id,
        user_id=access.user_id,
        store_id=access.store_id,
        created_at=access.created_at,
        updated_at=access.updated_at,
    )