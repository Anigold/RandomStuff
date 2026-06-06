from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    UpdateItemVendorInfoCommand,
    UpdateItemStoreInfoCommand
)


from workbot_core.application.use_cases.items.manage_items import ManageItems
from workbot_core.application.use_cases.manage_item_vendor_information import ManageItemVendorInformation
from workbot_core.application.use_cases.manage_item_store_information import ManageItemStoreInformation

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

from apps.api.auth.dependencies import (
    get_current_user,
    get_effective_store_scope,
    require_supervisor,
)
from workbot_core.domain.models.user import User, UserRole


router = APIRouter(prefix="/items", tags=["items"])


# @router.get("", response_model=list[ItemResponse])
# def list_items(
#     search: str | None = None,
#     include_inactive: bool = True,
#     store: str | None = None,
#     session: Session = Depends(get_db_session),
# ) -> list[ItemResponse]:
#     items = SqlItemRepository(session)
#     stores = SqlStoreRepository(session)
#     item_store_infos = SqlItemStoreInfoRepository(session)

#     if store:
#         store_obj = stores.get_by_name(store)

#         if store_obj is None:
#             raise HTTPException(status_code=404, detail=f"Store not found: {store}")

#         store_infos = item_store_infos.list_for_store(store_obj.id)
#         store_item_ids = {info.item_id for info in store_infos}

#         item_list = [
#             item
#             for item in items.list_all()
#             if item.id in store_item_ids
#         ]
#     else:
#         item_list = items.list_all()

#     if not include_inactive:
#         item_list = [item for item in item_list if item.is_active]

#     if search:
#         search_lower = search.casefold()
#         item_list = [
#             item
#             for item in item_list
#             if search_lower in item.name.casefold()
#         ]

#     return [_item_response(item) for item in item_list]

@router.get("", response_model=list[ItemResponse])
def list_items(
    search: str | None = None,
    include_inactive: bool = True,
    store: str | None = None,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[ItemResponse]:
    items = SqlItemRepository(session)
    item_store_infos = SqlItemStoreInfoRepository(session)

    effective_store = get_effective_store_scope(
        requested_store_name=store,
        current_user=current_user,
        session=session,
    )

    if effective_store is not None:
        store_infos = item_store_infos.list_for_store(effective_store.id)
        store_item_ids = {
            info.item_id
            for info in store_infos
            if info.is_active
        }

        item_list = [
            item
            for item in items.list_all()
            if item.id in store_item_ids
        ]
    else:
        item_list = items.list_all()

    if not include_inactive:
        item_list = [item for item in item_list if item.is_active]

    if search:
        search_lower = search.casefold()
        item_list = [
            item
            for item in item_list
            if search_lower in item.name.casefold()
        ]

    return [_item_response(item) for item in item_list]

# @router.get("/{item_id}", response_model=ItemDetailResponse)
# def get_item(
#     item_id: str,
#     session: Session = Depends(get_db_session),
# ) -> ItemDetailResponse:
#     try:
#         item = ManageItems(
#             items=SqlItemRepository(session),
#         ).get_item(item_id)

#     except ValueError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc

#     vendor_infos = SqlItemVendorInfoRepository(session)
#     store_infos = SqlItemStoreInfoRepository(session)

#     return ItemDetailResponse(
#         **_item_response(item).model_dump(),
#         vendor_info=[
#             _item_vendor_info_response(info)
#             for info in vendor_infos.list_for_item(item.id)
#         ],
#         store_info=[
#             _item_store_info_response(info)
#             for info in store_infos.list_for_item(item.id)
#         ],
#     )

@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item(
    item_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
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

    if current_user.role == UserRole.STORE:
        matching_store_infos = [
            info
            for info in all_store_infos
            if info.store_id == current_user.store_id and info.is_active
        ]

        if not matching_store_infos:
            raise HTTPException(
                status_code=403,
                detail="Cannot access item for another store.",
            )

        return ItemDetailResponse(
            **_item_response(item).model_dump(),
            vendor_info=[],
            store_info=[
                _item_store_info_response(info)
                for info in matching_store_infos
            ],
        )

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

@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    request: CreateItemRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_supervisor),
) -> ItemResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemVendorInfoResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemStoreInfoResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemVendorInfoResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemStoreInfoResponse:
    try:
        info = ManageItemStoreInformation(
            item_store_infos=SqlItemStoreInfoRepository(session),
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
    current_user: User = Depends(require_supervisor),
) -> ItemVendorInfoResponse:
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
    current_user: User = Depends(require_supervisor),
) -> ItemStoreInfoResponse:
    try:
        info = ManageItemStoreInformation(
            item_store_infos=SqlItemStoreInfoRepository(session),
        ).deactivate_store_info(
            item_id=item_id,
            info_id=info_id,
        )

        session.commit()

        return _item_store_info_response(info)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    
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