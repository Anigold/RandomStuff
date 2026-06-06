from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from apps.api.auth.sessions import SESSION_COOKIE_NAME, read_session_token
from apps.api.dependencies import get_db_session
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.user import User, UserRole
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
    SqlUserStoreAccessRepository,
)


def get_current_user(
    request: Request,
    session: Session = Depends(get_db_session),
) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    payload = read_session_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        )

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        )

    user = SqlUserRepository(session).get_by_id(str(user_id))

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return user


def require_supervisor(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.SUPERVISOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required.",
        )

    return user


def require_manager_or_supervisor(
    user: User = Depends(get_current_user),
) -> User:
    if user.role not in {UserRole.SUPERVISOR, UserRole.MANAGER}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required.",
        )

    return user


def get_accessible_store_ids(
    *,
    current_user: User,
    session: Session,
) -> set[str] | None:
    """Return None for supervisor meaning all stores are accessible."""

    if current_user.role == UserRole.SUPERVISOR:
        return None

    return set(
        SqlUserStoreAccessRepository(session).list_store_ids_for_user(
            current_user.id
        )
    )


def user_can_access_store(
    *,
    current_user: User,
    store_id: str,
    session: Session,
) -> bool:
    accessible_store_ids = get_accessible_store_ids(
        current_user=current_user,
        session=session,
    )

    if accessible_store_ids is None:
        return True

    return store_id in accessible_store_ids


def get_effective_store_scope(
    *,
    requested_store_name: str | None,
    current_user: User,
    session: Session,
) -> Store | None:
    stores = SqlStoreRepository(session)

    if current_user.role == UserRole.SUPERVISOR:
        if requested_store_name is None:
            return None

        store = stores.get_by_name(requested_store_name)

        if store is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store not found: {requested_store_name}",
            )

        return store

    accessible_store_ids = get_accessible_store_ids(
        current_user=current_user,
        session=session,
    ) or set()

    if not accessible_store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to any stores.",
        )

    if requested_store_name is None:
        if len(accessible_store_ids) == 1:
            store_id = next(iter(accessible_store_ids))
            store = stores.get_by_id(store_id)

            if store is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Assigned store not found.",
                )

            return store

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store scope is required.",
        )

    requested_store = stores.get_by_name(requested_store_name)

    if requested_store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store not found: {requested_store_name}",
        )

    if requested_store.id not in accessible_store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access this store.",
        )

    return requested_store

