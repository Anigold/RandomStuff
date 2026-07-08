from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import StoreScope, get_store_scope
from apps.api.auth.scope_guards import require_single_store_scope
from apps.api.dependencies import get_db_session
from apps.api.schemas.inventory_schema import (
    CreateInventoryCountRequest,
    InventoryCountLineRequest,
    InventoryCountLineResponse,
    InventoryCountResponse,
    InventoryItemResponse,
    UpdateInventoryCountRequest,
)

from workbot_core.domain.models.inventory import (
    InventoryCount,
    InventoryCountLine,
    InventoryCountStatus,
)

from workbot_core.infrastructure.database.repositories.inventory_repository import (
    SqlInventoryCountRepository,
)
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_store_info_repository import (
    SqlItemStoreInfoRepository,
)
from workbot_core.utils.ids import IdGenerator

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/items", response_model=list[InventoryItemResponse])
def list_inventory_items(
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> list[InventoryItemResponse]:
    store_id = require_single_store_scope(scope)

    item_repository = SqlItemRepository(session)
    item_store_info_repository = SqlItemStoreInfoRepository(session)

    store_infos = item_store_info_repository.list_for_store(store_id)
    active_item_ids = {
        info.item_id
        for info in store_infos
        if info.is_active
    }

    items = [
        item
        for item in item_repository.list_all()
        if item.id in active_item_ids and item.is_active
    ]

    return [
        InventoryItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            subcategory=item.subcategory,
            count_unit_quantity=item.count_unit_quantity,
            count_unit_measure=item.count_unit_measure,
            is_active=item.is_active,
        )
        for item in items
    ]


@router.post("/counts", response_model=InventoryCountResponse, status_code=201)
def create_inventory_count(
    request: CreateInventoryCountRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> InventoryCountResponse:
    store_id = require_single_store_scope(scope)

    _validate_count_lines_belong_to_store(
        request.lines,
        store_id=store_id,
        session=session,
    )

    repository = SqlInventoryCountRepository(session)

    count_id = IdGenerator.inventory_count_id(exists=repository.exists)

    now = datetime.now(UTC).replace(tzinfo=None)

    count = InventoryCount(
        id=count_id,
        store_id=store_id,
        count_date=request.count_date,
        notes=request.notes,
        created_at=now,
        updated_at=now,
        lines=tuple(
            InventoryCountLine(
                id=IdGenerator.inventory_count_line_id(),
                inventory_count_id=count_id,
                item_id=line.item_id,
                quantity=line.quantity,
                unit=line.unit,
                notes=line.notes,
                created_at=now,
                updated_at=now,
            )
            for line in request.lines
        ),
    )

    repository.save(count)
    session.commit()

    saved_count = repository.get_by_id(count.id)

    if saved_count is None:
        raise HTTPException(
            status_code=500,
            detail="Inventory count was not saved.",
        )

    return _inventory_count_response(saved_count, session=session)


@router.get("/counts", response_model=list[InventoryCountResponse])
def list_inventory_counts(
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> list[InventoryCountResponse]:
    store_id = require_single_store_scope(scope)

    counts = SqlInventoryCountRepository(session).list_for_store(store_id)

    return [
        _inventory_count_response(count, session=session)
        for count in counts
    ]


@router.get("/counts/{count_id}", response_model=InventoryCountResponse)
def get_inventory_count(
    count_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> InventoryCountResponse:
    store_id = require_single_store_scope(scope)

    count = SqlInventoryCountRepository(session).get_by_id(count_id)

    if count is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory count not found.",
        )

    if count.store_id != store_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot access inventory count for another store.",
        )

    return _inventory_count_response(count, session=session)


@router.put("/counts/{count_id}", response_model=InventoryCountResponse)
def update_inventory_count(
    count_id: str,
    request: UpdateInventoryCountRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> InventoryCountResponse:
    store_id = require_single_store_scope(scope)

    repository = SqlInventoryCountRepository(session)
    count = repository.get_by_id(count_id)

    if count is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory count not found.",
        )

    if count.store_id != store_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot update inventory count for another store.",
        )

    if count.status == InventoryCountStatus.SUBMITTED:
        raise HTTPException(
            status_code=400,
            detail="Submitted inventory counts cannot be updated.",
        )

    _validate_count_lines_belong_to_store(
        request.lines,
        store_id=store_id,
        session=session,
    )

    now = datetime.now(UTC).replace(tzinfo=None)

    updated_count = count.update_draft(
        count_date=request.count_date,
        notes=request.notes,
        updated_at=now,
        lines=tuple(
            InventoryCountLine(
                id=IdGenerator.inventory_count_line_id(),
                inventory_count_id=count.id,
                item_id=line.item_id,
                quantity=line.quantity,
                unit=line.unit,
                notes=line.notes,
                created_at=now,
                updated_at=now,
            )
            for line in request.lines
        ),
    )

    repository.save(updated_count)
    session.commit()

    saved_count = repository.get_by_id(count_id)

    if saved_count is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory count not found.",
        )

    return _inventory_count_response(saved_count, session=session)


@router.post("/counts/{count_id}/submit", response_model=InventoryCountResponse)
def submit_inventory_count(
    count_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> InventoryCountResponse:
    store_id = require_single_store_scope(scope)

    repository = SqlInventoryCountRepository(session)
    count = repository.get_by_id(count_id)

    if count is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory count not found.",
        )

    if count.store_id != store_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot submit inventory count for another store.",
        )

    submitted_count = replace(
        count.submit(),
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )

    repository.save(submitted_count)
    session.commit()

    saved_count = repository.get_by_id(count_id)

    if saved_count is None:
        raise HTTPException(
            status_code=404,
            detail="Inventory count not found.",
        )

    return _inventory_count_response(saved_count, session=session)


def _validate_count_lines_belong_to_store(
    lines: list[InventoryCountLineRequest],
    *,
    store_id: str,
    session: Session,
) -> None:
    item_store_info_repository = SqlItemStoreInfoRepository(session)

    active_item_ids = {
        info.item_id
        for info in item_store_info_repository.list_for_store(store_id)
        if info.is_active
    }

    invalid_item_ids = [
        line.item_id
        for line in lines
        if line.item_id not in active_item_ids
    ]

    if invalid_item_ids:
        raise HTTPException(
            status_code=400,
            detail=(
                "Inventory count contains items not available to this store: "
                + ", ".join(sorted(set(invalid_item_ids)))
            ),
        )


def _inventory_count_response(
    count: InventoryCount,
    *,
    session: Session,
) -> InventoryCountResponse:
    item_repository = SqlItemRepository(session)
    items_by_id = {
        item.id: item
        for item in item_repository.list_all()
    }

    return InventoryCountResponse(
        id=count.id,
        store_id=count.store_id,
        count_date=count.count_date,
        status=count.status.value,
        notes=count.notes,
        lines=[
            InventoryCountLineResponse(
                id=line.id,
                inventory_count_id=line.inventory_count_id,
                item_id=line.item_id,
                item_name=(
                    items_by_id[line.item_id].name
                    if line.item_id in items_by_id
                    else None
                ),
                quantity=line.quantity,
                unit=line.unit,
                notes=line.notes,
                created_at=line.created_at,
                updated_at=line.updated_at,
            )
            for line in count.lines
        ],
        created_at=count.created_at,
        updated_at=count.updated_at,
    )