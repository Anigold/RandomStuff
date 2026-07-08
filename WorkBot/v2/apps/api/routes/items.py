from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.auth.dependencies import StoreScope, get_store_scope
from apps.api.dependencies import get_db_session
from apps.api.schemas.item_schema import (
    AddItemStoreInfoRequest,
    AddItemVendorInfoRequest,
    CreateItemRequest,
    ItemDetailResponse,
    ItemResponse,
    ItemStoreInfoResponse,
    ItemVendorInfoResponse,
    UpdateItemRequest,
    UpdateItemStoreInfoRequest,
    UpdateItemVendorInfoRequest,
)
from workbot_core.application.dto.item_catalog_commands import (
    AddItemStoreInfoCommand,
    AddItemVendorInfoCommand,
    CreateItemCommand,
    UpdateItemCommand,
    UpdateItemStoreInfoCommand,
    UpdateItemVendorInfoCommand,
)
from workbot_core.application.use_cases.items.manage_items import ManageItems
from workbot_core.application.use_cases.manage_item_store_information import (
    ManageItemStoreInformation,
)
from workbot_core.application.use_cases.manage_item_vendor_information import (
    ManageItemVendorInformation,
)
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_store_info_repository import (
    SqlItemStoreInfoRepository,
)
from workbot_core.infrastructure.database.repositories.item_vendor_info_repository import (
    SqlItemVendorInfoRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemResponse])
def list_items(
    search: str | None = None,
    include_inactive: bool = True,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> list[ItemResponse]:
    items = SqlItemRepository(session)
    

    if scope.is_supervisor_scope:
        item_list = items.list_all()

    else:
        item_store_infos = SqlItemStoreInfoRepository(session)
        store_item_ids = _item_ids_for_scope(
            item_store_infos=item_store_infos,
            scope=scope,
            active_store_info_only=True,
        )

        item_list = [
            item
            for item in items.list_all()
            if item.id in store_item_ids
        ]

    if not include_inactive:
        item_list = [
            item
            for item in item_list
            if item.is_active
        ]

    if search:
        search_lower = search.casefold()
        item_list = [
            item
            for item in item_list
            if search_lower in item.name.casefold()
        ]

    return [
        _item_response(item)
        for item in item_list
    ]


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item(
    item_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemDetailResponse:
    try:
        item = ManageItems(
            items=SqlItemRepository(session),
        ).get_item(item_id)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    vendor_infos = SqlItemVendorInfoRepository(session)
    store_infos = SqlItemStoreInfoRepository(session)

    all_store_infos = store_infos.list_for_item(item.id)

    if scope.is_supervisor_scope:
        return ItemDetailResponse(
            **_item_response(item).model_dump(),
            vendor_info=[
                _item_vendor_info_response(info)
                for info in vendor_infos.list_for_item(item.id)
            ],
            store_info=[
                _item_store_info_response(info)
                for info in all_store_infos
            ],
        )

    scoped_store_infos = [
        info
        for info in all_store_infos
        if info.store_id in scope.real_store_ids
        and info.is_active
    ]

    if not scoped_store_infos:
        raise HTTPException(
            status_code=403,
            detail="Cannot access item for selected operating scope.",
        )

    return ItemDetailResponse(
        **_item_response(item).model_dump(),
        vendor_info=[],
        store_info=[
            _item_store_info_response(info)
            for info in scoped_store_infos
        ],
    )


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    request: CreateItemRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemResponse:
    _require_supervisor_scope(scope)

    try:
        item = ManageItems(
            items=SqlItemRepository(session),
        ).create_item(
            CreateItemCommand(
                name=request.name,
                category=request.category,
                subcategory=request.subcategory,
                count_unit_quantity=request.count_unit_quantity,
                count_unit_measure=request.count_unit_measure,
                custom_each_name=request.custom_each_name,
                each_quantity=request.each_quantity,
                each_measure=request.each_measure,
                weight_quantity=request.weight_quantity,
                weight_measure=request.weight_measure,
                volume_quantity=request.volume_quantity,
                volume_measure=request.volume_measure,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_response(item)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: str,
    request: UpdateItemRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemResponse:
    _require_supervisor_scope(scope)

    try:
        item = ManageItems(
            items=SqlItemRepository(session),
        ).update_item(
            UpdateItemCommand(
                item_id=item_id,
                name=request.name,
                category=request.category,
                subcategory=request.subcategory,
                count_unit_quantity=request.count_unit_quantity,
                count_unit_measure=request.count_unit_measure,
                custom_each_name=request.custom_each_name,
                each_quantity=request.each_quantity,
                each_measure=request.each_measure,
                weight_quantity=request.weight_quantity,
                weight_measure=request.weight_measure,
                volume_quantity=request.volume_quantity,
                volume_measure=request.volume_measure,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_response(item)

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.delete("/{item_id}", response_model=ItemResponse)
def delete_item(
    item_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemResponse:
    _require_supervisor_scope(scope)

    try:
        item = ManageItems(
            items=SqlItemRepository(session),
        ).deactivate_item(item_id)

        session.commit()

        return _item_response(item)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/{item_id}/vendor-info",
    response_model=ItemVendorInfoResponse,
    status_code=201,
)
def add_item_vendor_info(
    item_id: str,
    request: AddItemVendorInfoRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemVendorInfoResponse:
    _require_supervisor_scope(scope)

    try:
        info = ManageItemVendorInformation(
            items=SqlItemRepository(session),
            vendors=SqlVendorRepository(session),
            item_vendor_infos=SqlItemVendorInfoRepository(session),
        ).add_vendor_info(
            AddItemVendorInfoCommand(
                item_id=item_id,
                vendor_id=request.vendor_id,
                vendor_sku=request.vendor_sku,
                purchase_unit=request.purchase_unit,
                pack_size=request.pack_size,
                price=request.price,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_vendor_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{item_id}/store-info",
    response_model=ItemStoreInfoResponse,
    status_code=201,
)
def add_item_store_info(
    item_id: str,
    request: AddItemStoreInfoRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemStoreInfoResponse:
    _require_store_in_scope(
        store_id=request.store_id,
        scope=scope,
    )

    try:
        info = ManageItemStoreInformation(
            items=SqlItemRepository(session),
            stores=SqlStoreRepository(session),
            item_store_infos=SqlItemStoreInfoRepository(session),
        ).add_store_info(
            AddItemStoreInfoCommand(
                item_id=item_id,
                store_id=request.store_id,
                count_unit=request.count_unit,
                par=request.par,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_store_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put(
    "/{item_id}/vendor-info/{info_id}",
    response_model=ItemVendorInfoResponse,
)
def update_item_vendor_info(
    item_id: str,
    info_id: str,
    request: UpdateItemVendorInfoRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemVendorInfoResponse:
    _require_supervisor_scope(scope)

    try:
        info = ManageItemVendorInformation(
            item_vendor_infos=SqlItemVendorInfoRepository(session),
        ).update_vendor_info(
            UpdateItemVendorInfoCommand(
                item_id=item_id,
                info_id=info_id,
                vendor_sku=request.vendor_sku,
                purchase_unit=request.purchase_unit,
                pack_size=request.pack_size,
                price=request.price,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_vendor_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put(
    "/{item_id}/store-info/{info_id}",
    response_model=ItemStoreInfoResponse,
)
def update_item_store_info(
    item_id: str,
    info_id: str,
    request: UpdateItemStoreInfoRequest,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemStoreInfoResponse:
    item_store_infos = SqlItemStoreInfoRepository(session)

    existing_info = _get_item_store_info_or_404(
        item_store_infos=item_store_infos,
        item_id=item_id,
        info_id=info_id,
    )

    _require_store_in_scope(
        store_id=existing_info.store_id,
        scope=scope,
    )

    try:
        info = ManageItemStoreInformation(
            item_store_infos=item_store_infos,
        ).update_store_info(
            UpdateItemStoreInfoCommand(
                item_id=item_id,
                info_id=info_id,
                count_unit=request.count_unit,
                par=request.par,
                is_active=request.is_active,
            )
        )

        session.commit()

        return _item_store_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/{item_id}/vendor-info/{info_id}",
    response_model=ItemVendorInfoResponse,
)
def delete_item_vendor_info(
    item_id: str,
    info_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemVendorInfoResponse:
    _require_supervisor_scope(scope)

    try:
        info = ManageItemVendorInformation(
            item_vendor_infos=SqlItemVendorInfoRepository(session),
        ).deactivate_vendor_info(
            item_id=item_id,
            info_id=info_id,
        )

        session.commit()

        return _item_vendor_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/{item_id}/store-info/{info_id}",
    response_model=ItemStoreInfoResponse,
)
def delete_item_store_info(
    item_id: str,
    info_id: str,
    session: Session = Depends(get_db_session),
    scope: StoreScope = Depends(get_store_scope),
) -> ItemStoreInfoResponse:
    item_store_infos = SqlItemStoreInfoRepository(session)

    existing_info = _get_item_store_info_or_404(
        item_store_infos=item_store_infos,
        item_id=item_id,
        info_id=info_id,
    )

    _require_store_in_scope(
        store_id=existing_info.store_id,
        scope=scope,
    )

    try:
        info = ManageItemStoreInformation(
            item_store_infos=item_store_infos,
        ).deactivate_store_info(
            item_id=item_id,
            info_id=info_id,
        )

        session.commit()

        return _item_store_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _require_supervisor_scope(scope: StoreScope) -> None:
    if not scope.is_supervisor_scope:
        raise HTTPException(
            status_code=403,
            detail="Supervisor scope required.",
        )


def _require_store_in_scope(
    *,
    store_id: str,
    scope: StoreScope,
) -> None:
    if store_id not in scope.real_store_ids:
        raise HTTPException(
            status_code=403,
            detail="Selected scope cannot modify this store.",
        )


def _item_ids_for_scope(
    *,
    item_store_infos: SqlItemStoreInfoRepository,
    scope: StoreScope,
    active_store_info_only: bool,
) -> set[str]:
    item_ids: set[str] = set()

    for store_id in scope.real_store_ids:
        store_infos = item_store_infos.list_for_store(store_id)

        item_ids.update(
            info.item_id
            for info in store_infos
            if not active_store_info_only or info.is_active
        )

    return item_ids


def _get_item_store_info_or_404(
    *,
    item_store_infos: SqlItemStoreInfoRepository,
    item_id: str,
    info_id: str,
):
    for info in item_store_infos.list_for_item(item_id):
        if info.id == info_id:
            return info

    raise HTTPException(
        status_code=404,
        detail="Item store info not found.",
    )


def _http_error_from_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)

    if "not found" in message.casefold():
        return HTTPException(status_code=404, detail=message)

    return HTTPException(status_code=400, detail=message)


def _item_response(item) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        subcategory=item.subcategory,
        count_unit_quantity=item.count_unit_quantity,
        count_unit_measure=item.count_unit_measure,
        custom_each_name=item.custom_each_name,
        each_quantity=item.each_quantity,
        each_measure=item.each_measure,
        weight_quantity=item.weight_quantity,
        weight_measure=item.weight_measure,
        volume_quantity=item.volume_quantity,
        volume_measure=item.volume_measure,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _item_vendor_info_response(info) -> ItemVendorInfoResponse:
    return ItemVendorInfoResponse(
        id=info.id,
        item_id=info.item_id,
        vendor_id=info.vendor_id,
        vendor_sku=info.vendor_sku,
        purchase_unit=info.purchase_unit,
        pack_size=info.pack_size,
        price=info.price,
        last_purchase_date=info.last_purchase_date,
        is_active=info.is_active,
        created_at=info.created_at,
        updated_at=info.updated_at,
    )


def _item_store_info_response(info) -> ItemStoreInfoResponse:
    return ItemStoreInfoResponse(
        id=info.id,
        item_id=info.item_id,
        store_id=info.store_id,
        count_unit=info.count_unit,
        par=info.par,
        is_active=info.is_active,
        created_at=info.created_at,
        updated_at=info.updated_at,
    )