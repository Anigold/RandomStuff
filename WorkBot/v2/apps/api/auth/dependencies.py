from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID
from apps.api.auth.tokens import AuthTokenError, decode_token
from apps.api.dependencies import get_db_session, get_settings
from workbot_core.config.settings import Settings
from workbot_core.domain.models.user import User
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
    SqlUserStoreAccessRepository,
)


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class StoreScope:
    requested_scope_id: str | None
    real_store_ids: list[str]
    is_supervisor_scope: bool = False


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_token(
            token=credentials.credentials,
            expected_token_type="access",
            secret_key=settings.auth_secret_key,
            algorithm=settings.auth_jwt_algorithm,
        )
    except AuthTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from None

    user_repository = SqlUserRepository(db)
    user = user_repository.get_by_id(payload.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def user_can_use_supervisor_scope(user: User) -> bool:
    role = getattr(user, "role", None)

    if role is None:
        return False

    role_value = getattr(role, "value", role)
    normalized_role = str(role_value).casefold()

    return normalized_role in {
        "supervisor",
        "super_admin",
        "admin",
    }


def get_all_store_ids(db: Session) -> list[str]:
    store_repository = SqlStoreRepository(db)

    return [
        store.id
        for store in store_repository.list_all()
        if getattr(store, "is_active", True)
    ]


def get_accessible_store_ids_for_user(
    *,
    user_id: str,
    db: Session,
) -> list[str]:
    access_repository = SqlUserStoreAccessRepository(db)

    return access_repository.list_store_ids_for_user(user_id)


def resolve_store_scope(
    *,
    current_user: User,
    db: Session,
    scope_id: str | None,
) -> StoreScope:
    """
    Convert a requested UI scope into real store IDs.

    scope_id=None:
        Uses the user's assigned stores.

    scope_id="sto_123":
        Uses one real store if the user has access.

    scope_id="__supervisor__":
        Uses all real stores if the user can use supervisor scope.
    """
    if scope_id == SUPERVISOR_SCOPE_ID:
        if not user_can_use_supervisor_scope(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor scope required.",
            )

        return StoreScope(
            requested_scope_id=scope_id,
            real_store_ids=get_all_store_ids(db),
            is_supervisor_scope=True,
        )

    accessible_store_ids = get_accessible_store_ids_for_user(
        user_id=current_user.id,
        db=db,
    )

    if scope_id is None:
        return StoreScope(
            requested_scope_id=None,
            real_store_ids=accessible_store_ids,
            is_supervisor_scope=False,
        )

    if scope_id not in accessible_store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this store.",
        )

    return StoreScope(
        requested_scope_id=scope_id,
        real_store_ids=[scope_id],
        is_supervisor_scope=False,
    )


def get_store_scope(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    scope_id: Annotated[str | None, Query()] = None,
) -> StoreScope:
    return resolve_store_scope(
        current_user=current_user,
        db=db,
        scope_id=scope_id,
    )