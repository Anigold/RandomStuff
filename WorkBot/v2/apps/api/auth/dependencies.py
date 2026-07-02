from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from apps.api.auth.tokens import AuthTokenError, decode_token
from apps.api.dependencies import get_db_session, get_settings
from workbot_core.config.settings import Settings
from workbot_core.domain.models.user import User
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
    SqlUserStoreAccessRepository,
)


bearer_scheme = HTTPBearer(auto_error=False)


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


def _user_is_supervisor(user: User) -> bool:
    """
    Temporary compatibility helper.

    Adjust this once the final User domain permission shape is settled.
    Supports common field names so routes do not need to care.
    """
    if getattr(user, "is_supervisor", False):
        return True

    if getattr(user, "is_admin", False):
        return True

    role = getattr(user, "role", None)

    if role is None:
        return False

    return str(role).lower() in {
        "admin",
        "supervisor",
        "manager",
        "owner",
    }


def require_supervisor(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not _user_is_supervisor(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor access required",
        )

    return current_user


def user_can_access_store(
    *,
    user_id: str,
    store_id: str,
    db: Session,
) -> bool:
    access_repository = SqlUserStoreAccessRepository(db)

    return access_repository.user_has_store_access(
        user_id=user_id,
        store_id=store_id,
    )


def get_accessible_store_ids_for_user(
    *,
    user_id: str,
    db: Session,
) -> list[str]:
    access_repository = SqlUserStoreAccessRepository(db)

    return access_repository.list_store_ids_for_user(user_id)


def get_effective_store_scope(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    store_id: Annotated[str | None, Query()] = None,
) -> list[str]:
    """
    Returns the list of store IDs the request should operate against.

    If store_id is provided:
        - verify the user can access that store
        - return [store_id]

    If store_id is not provided:
        - return all store IDs available to the user
    """
    accessible_store_ids = get_accessible_store_ids_for_user(
        user_id=current_user.id,
        db=db,
    )

    if store_id is None:
        return accessible_store_ids

    if store_id not in accessible_store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this store",
        )

    return [store_id]