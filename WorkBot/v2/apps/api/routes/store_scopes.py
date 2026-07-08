from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import (
    get_accessible_store_ids_for_user,
    get_current_user,
    user_can_use_supervisor_scope,
)
from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID
from apps.api.dependencies import get_db_session
from apps.api.schemas.scope_schema import StoreScopeResponse
from workbot_core.domain.models.user import User
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)


router = APIRouter(prefix="/store-scopes", tags=["store-scopes"])


@router.get("", response_model=list[StoreScopeResponse])
def list_store_scopes(
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[StoreScopeResponse]:
    store_repository = SqlStoreRepository(session)

    accessible_store_ids = set(
        get_accessible_store_ids_for_user(
            user_id=current_user.id,
            db=session,
        )
    )

    stores = [
        store
        for store in store_repository.list_all()
        if store.id in accessible_store_ids
        and getattr(store, "is_active", True)
    ]

    scopes: list[StoreScopeResponse] = []

    if user_can_use_supervisor_scope(current_user):
        scopes.append(
            StoreScopeResponse(
                id=SUPERVISOR_SCOPE_ID,
                name="Supervisor",
                type="supervisor",
            )
        )

    scopes.extend(
        StoreScopeResponse(
            id=store.id,
            name=store.name,
            type="store",
        )
        for store in stores
    )

    return scopes