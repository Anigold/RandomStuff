from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dataclasses import replace

from apps.api.dependencies import get_db_session
from apps.api.schemas.item_schema import (
    AddItemStoreInfoRequest,
    AddItemVendorInfoRequest,
    CreateItemRequest,
    ItemDetailResponse,
    ItemResponse,
    ItemStoreInfoResponse,
    ItemVendorInfoResponse,
)
from workbot_core.application.dto.item_catalog_commands import (
    AddItemStoreInfoCommand,
    AddItemVendorInfoCommand,
    CreateItemCommand,
)
from workbot_core.application.use_cases.add_item_store_information import AddItemStoreInfo
from workbot_core.application.use_cases.add_item_vendor_information import AddItemVendorInfo
from workbot_core.application.use_cases.create_item import CreateItem
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

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemResponse])
def list_items(
    search: str | None = None,
    session: Session = Depends(get_db_session),
) -> list[ItemResponse]:
    items = SqlItemRepository(session)
    all_items = items.list_all()

    if search:
        normalized = search.casefold().strip()
        all_items = [
            item for item in all_items
            if normalized in item.name.casefold()
        ]

    return [_item_response(item) for item in all_items]


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item(
    item_id: str,
    session: Session = Depends(get_db_session),
) -> ItemDetailResponse:
    items = SqlItemRepository(session)
    vendor_infos = SqlItemVendorInfoRepository(session)
    store_infos = SqlItemStoreInfoRepository(session)

    item = items.get_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail=f"Item not found: {item_id}")

    return ItemDetailResponse(
        **_item_response(item).model_dump(),
        vendor_info=[
            _item_vendor_info_response(info)
            for info in vendor_infos.list_for_item(item.id)
        ],
        store_info=[
            _item_store_info_response(info)
            for info in store_infos.list_for_item(item.id)
        ],
    )


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    request: CreateItemRequest,
    session: Session = Depends(get_db_session),
) -> ItemResponse:
    try:
        item = CreateItem(
            items=SqlItemRepository(session),
        ).run(
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


@router.post(
    "/{item_id}/vendor-info",
    response_model=ItemVendorInfoResponse,
    status_code=201,
)
def add_item_vendor_info(
    item_id: str,
    request: AddItemVendorInfoRequest,
    session: Session = Depends(get_db_session),
) -> ItemVendorInfoResponse:
    try:
        info = AddItemVendorInfo(
            items=SqlItemRepository(session),
            vendors=SqlVendorRepository(session),
            item_vendor_infos=SqlItemVendorInfoRepository(session),
        ).run(
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
) -> ItemStoreInfoResponse:
    try:
        info = AddItemStoreInfo(
            items=SqlItemRepository(session),
            stores=SqlStoreRepository(session),
            item_store_infos=SqlItemStoreInfoRepository(session),
        ).run(
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

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: str,
    request: UpdateItemRequest,
    session: Session = Depends(get_db_session),
) -> ItemResponse:
    items = SqlItemRepository(session)

    item = items.get_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail=f"Item not found: {item_id}")

    try:
        updated = replace(
            item,
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

        items.save(updated)
        session.commit()

        return _item_response(updated)

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
) -> ItemVendorInfoResponse:
    item_vendor_infos = SqlItemVendorInfoRepository(session)

    info = item_vendor_infos.get_by_id(info_id)

    if info is None or info.item_id != item_id:
        raise HTTPException(
            status_code=404,
            detail=f"Item vendor info not found: {info_id}",
        )

    updated = replace(
        info,
        vendor_sku=request.vendor_sku,
        purchase_unit=request.purchase_unit,
        pack_size=request.pack_size,
        price=request.price,
        is_active=request.is_active,
    )

    item_vendor_infos.save(updated)
    session.commit()

    return _item_vendor_info_response(updated)


@router.put(
    "/{item_id}/store-info/{info_id}",
    response_model=ItemStoreInfoResponse,
)
def update_item_store_info(
    item_id: str,
    info_id: str,
    request: UpdateItemStoreInfoRequest,
    session: Session = Depends(get_db_session),
) -> ItemStoreInfoResponse:
    item_store_infos = SqlItemStoreInfoRepository(session)

    info = item_store_infos.get_by_id(info_id)

    if info is None or info.item_id != item_id:
        raise HTTPException(
            status_code=404,
            detail=f"Item store info not found: {info_id}",
        )

    updated = replace(
        info,
        count_unit=request.count_unit,
        par=request.par,
        is_active=request.is_active,
    )

    item_store_infos.save(updated)
    session.commit()

    return _item_store_info_response(updated)

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