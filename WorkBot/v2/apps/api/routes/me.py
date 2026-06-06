from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import get_current_user
from apps.api.dependencies import get_db_session
from workbot_core.domain.models.user import User, UserRole
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserStoreAccessRepository,
)


router = APIRouter(prefix="/me", tags=["me"])


class CurrentUserStoreResponse(BaseModel):
    id: str
    name: str


class CurrentUserResponse(BaseModel):
    id: str
    username: str
    role: str
    stores: list[CurrentUserStoreResponse]
    can_use_supervisor_scope: bool


@router.get("", response_model=CurrentUserResponse)
def get_me(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> CurrentUserResponse:
    stores = SqlStoreRepository(session)

    if user.role == UserRole.SUPERVISOR:
        accessible_stores = stores.list_active()
        can_use_supervisor_scope = True
    else:
        user_store_accesses = SqlUserStoreAccessRepository(session)
        store_ids = user_store_accesses.list_store_ids_for_user(user.id)
        accessible_stores = [
            store
            for store in stores.list_active()
            if store.id in set(store_ids)
        ]
        can_use_supervisor_scope = False

    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        role=user.role.value,
        can_use_supervisor_scope=can_use_supervisor_scope,
        stores=[
            CurrentUserStoreResponse(
                id=store.id,
                name=store.name,
            )
            for store in accessible_stores
        ],
    )