from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Iterator

from fastapi import FastAPI

from apps.api.auth.dependencies import get_current_user
from workbot_core.domain.models.user import User, UserRole, UserStoreAccess


def make_test_user(
    *,
    user_id: str = "usr_test",
    username: str = "test-user",
    role: UserRole = UserRole.SUPERVISOR,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        username=username,
        password_hash="not-used-in-route-tests",
        role=role,
        is_active=is_active,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def make_supervisor_user(
    *,
    user_id: str = "usr_supervisor",
    username: str = "supervisor",
) -> User:
    return make_test_user(
        user_id=user_id,
        username=username,
        role=UserRole.SUPERVISOR,
    )


def make_manager_user(
    *,
    user_id: str = "usr_manager",
    username: str = "manager",
) -> User:
    return make_test_user(
        user_id=user_id,
        username=username,
        role=UserRole.MANAGER,
    )


def make_viewer_user(
    *,
    user_id: str = "usr_viewer",
    username: str = "viewer",
) -> User:
    return make_test_user(
        user_id=user_id,
        username=username,
        role=UserRole.VIEWER,
    )


def make_user_store_access(
    *,
    access_id: str = "usa_test",
    user_id: str,
    store_id: str,
) -> UserStoreAccess:
    return UserStoreAccess(
        id=access_id,
        user_id=user_id,
        store_id=store_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def make_user_store_accesses(
    *,
    user_id: str,
    store_ids: Iterable[str],
) -> list[UserStoreAccess]:
    return [
        make_user_store_access(
            access_id=f"usa_{index}",
            user_id=user_id,
            store_id=store_id,
        )
        for index, store_id in enumerate(store_ids, start=1)
    ]


def override_current_user(app: FastAPI, user: User) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def clear_current_user_override(app: FastAPI) -> None:
    app.dependency_overrides.pop(get_current_user, None)


@contextmanager
def authenticated_as(app: FastAPI, user: User) -> Iterator[User]:
    previous_override = app.dependency_overrides.get(get_current_user)

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        yield user
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = previous_override