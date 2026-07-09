# apps/api/routes/stores.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import StoreScope, get_store_scope
from apps.api.auth.scope_guards import require_supervisor_scope
from apps.api.dependencies import get_db_session
from apps.api.schemas.store_schema import (
    CreateStoreRequest,
    StoreResponse,
    UpdateStoreRequest,
)
from workbot_core.application.dto.store_commands import (
    CreateStoreCommand,
    UpdateStoreCommand,
)
from workbot_core.application.use_cases.stores.manage_stores import ManageStores
from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)


router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[StoreResponse])
def list_stores(
    search: str | None = None,
    include_inactive: bool = True,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> list[StoreResponse]:
    require_supervisor_scope(scope)

    stores = ManageStores(
        stores=SqlStoreRepository(session),
    ).list_stores(
        search=search,
        include_inactive=include_inactive,
    )

    return [_store_response(store) for store in stores]


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> StoreResponse:
    require_supervisor_scope(scope)

    try:
        store = ManageStores(
            stores=SqlStoreRepository(session),
        ).get_store(store_id)

        return _store_response(store)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=StoreResponse, status_code=201)
def create_store(
    request: CreateStoreRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> StoreResponse:
    require_supervisor_scope(scope)

    try:
        store = ManageStores(
            stores=SqlStoreRepository(session),
        ).create_store(
            CreateStoreCommand(
                name=request.name,
                is_active=request.is_active,
                general_manager=request.general_manager,
                inventory_clerk=request.inventory_clerk,
                address=request.address,
                phone_number=request.phone_number,
                special_notes=request.special_notes,
            )
        )

        session.commit()

        return _store_response(store)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    request: UpdateStoreRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> StoreResponse:
    require_supervisor_scope(scope)

    try:
        store = ManageStores(
            stores=SqlStoreRepository(session),
        ).update_store(
            UpdateStoreCommand(
                store_id=store_id,
                name=request.name,
                is_active=request.is_active,
                general_manager=request.general_manager,
                inventory_clerk=request.inventory_clerk,
                address=request.address,
                phone_number=request.phone_number,
                special_notes=request.special_notes,
            )
        )

        session.commit()

        return _store_response(store)

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.delete("/{store_id}", response_model=StoreResponse)
def delete_store(
    store_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> StoreResponse:
    require_supervisor_scope(scope)

    try:
        store = ManageStores(
            stores=SqlStoreRepository(session),
        ).deactivate_store(store_id)

        session.commit()

        return _store_response(store)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _http_error_from_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)

    if "not found" in message.casefold():
        return HTTPException(status_code=404, detail=message)

    return HTTPException(status_code=400, detail=message)


def _store_response(store: Store) -> StoreResponse:
    return StoreResponse(
        id=store.id,
        name=store.name,
        is_active=store.is_active,
        general_manager=store.general_manager,
        inventory_clerk=store.inventory_clerk,
        address=store.address,
        phone_number=store.phone_number,
        special_notes=store.special_notes or "",
        created_at=store.created_at,
        updated_at=store.updated_at,
    )