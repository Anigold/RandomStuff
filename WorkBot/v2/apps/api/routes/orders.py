from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from apps.api.schemas.order_schema import (
    CancelOrderRequest,
    CreateOrderLineRequest,
    CreateOrderRequest,
    OrderDetailResponse,
    OrderLineResponse,
    OrderListResponse,
    UpdateOrderNotesRequest,
)
from workbot_core.application.dto.order_commands import (
    CancelOrderCommand,
    CreateOrderCommand,
    CreateOrderLineCommand,
    UpdateOrderNotesCommand,
)
from workbot_core.application.use_cases.manage_orders import ManageOrders
from workbot_core.domain.models.order import Order
from workbot_core.domain.models.order_line import OrderLine
from workbot_core.infrastructure.database.repositories.order_repository import (
    SqlOrderRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderListResponse])
def list_orders(
    store: str | None = Query(default=None),
    vendor: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    session: Session = Depends(get_db_session),
) -> list[OrderListResponse]:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order_list = ManageOrders(
            orders=SqlOrderRepository(session),
            stores=stores,
            vendors=vendors,
        ).list_orders(
            store=store,
            vendor=vendor,
            start_date=start_date,
            end_date=end_date,
        )

        stores_by_id = {store.id: store for store in stores.list_all()}
        vendors_by_id = {vendor.id: vendor for vendor in vendors.list_all()}

        return [
            _order_list_response(
                order,
                store_name=stores_by_id.get(order.store_id).name
                if order.store_id in stores_by_id
                else None,
                vendor_name=vendors_by_id.get(order.vendor_id).name
                if order.vendor_id in vendors_by_id
                else None,
            )
            for order in order_list
        ]

    except ValueError as exc:
        raise _http_error_from_value_error(exc) from exc


@router.post("", response_model=OrderDetailResponse, status_code=201)
def create_order(
    request: CreateOrderRequest,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
            stores=stores,
            vendors=vendors,
        ).create_order(
            CreateOrderCommand(
                store_id=request.store_id,
                vendor_id=request.vendor_id,
                order_date=request.order_date,
                delivery_date=request.delivery_date,
                status=request.status,
                source=request.source,
                source_reference=request.source_reference,
                notes=request.notes,
                lines=tuple(
                    _create_order_line_command(line)
                    for line in request.lines
                ),
            )
        )

        session.commit()

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
        ).get_order(order_id)

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        raise _http_error_from_value_error(exc) from exc


@router.patch("/{order_id}/notes", response_model=OrderDetailResponse)
def update_order_notes(
    order_id: str,
    request: UpdateOrderNotesRequest,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
        ).update_notes(
            UpdateOrderNotesCommand(
                order_id=order_id,
                notes=request.notes,
            )
        )

        session.commit()

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.post("/{order_id}/cancel", response_model=OrderDetailResponse)
def cancel_order(
    order_id: str,
    request: CancelOrderRequest,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
        ).cancel_order(
            CancelOrderCommand(
                order_id=order_id,
                reason=request.reason,
            )
        )

        session.commit()

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.post("/{order_id}/export", response_model=OrderDetailResponse)
def mark_order_exported(
    order_id: str,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
        ).mark_exported(order_id)

        session.commit()

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.post("/{order_id}/fulfill", response_model=OrderDetailResponse)
def mark_order_fulfilled(
    order_id: str,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    try:
        order = ManageOrders(
            orders=SqlOrderRepository(session),
        ).mark_fulfilled(order_id)

        session.commit()

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

        return _order_detail_response(
            order,
            store_name=store.name if store else None,
            vendor_name=vendor.name if vendor else None,
        )

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: str,
    session: Session = Depends(get_db_session),
) -> None:
    try:
        ManageOrders(
            orders=SqlOrderRepository(session),
        ).delete_order(order_id)

        session.commit()

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


def _create_order_line_command(
    request: CreateOrderLineRequest,
) -> CreateOrderLineCommand:
    return CreateOrderLineCommand(
        source_item_name=request.source_item_name,
        source_vendor_sku=request.source_vendor_sku,
        item_id=request.item_id,
        item_vendor_info_id=request.item_vendor_info_id,
        item_name_snapshot=request.item_name_snapshot,
        vendor_sku_snapshot=request.vendor_sku_snapshot,
        unit_price_snapshot=request.unit_price_snapshot,
        quantity=request.quantity,
        unit=request.unit,
        notes=request.notes,
    )


def _order_list_response(
    order: Order,
    *,
    store_name: str | None = None,
    vendor_name: str | None = None,
) -> OrderListResponse:
    return OrderListResponse(
        id=order.id,
        store_id=order.store_id,
        store_name=store_name,
        vendor_id=order.vendor_id,
        vendor_name=vendor_name,
        order_date=order.order_date,
        delivery_date=order.delivery_date,
        status=order.status.value,
        source=order.source,
        source_reference=order.source_reference,
        line_count=len(order.lines),
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def _order_detail_response(
    order: Order,
    *,
    store_name: str | None = None,
    vendor_name: str | None = None,
) -> OrderDetailResponse:
    return OrderDetailResponse(
        **_order_list_response(
            order,
            store_name=store_name,
            vendor_name=vendor_name,
        ).model_dump(),
        notes=order.notes or "",
        lines=[
            _order_line_response(line)
            for line in order.lines
        ],
    )


def _order_line_response(line: OrderLine) -> OrderLineResponse:
    return OrderLineResponse(
        id=line.id,
        order_id=line.order_id,
        status=line.status.value,
        status_reason=line.status_reason,
        source_item_name=line.source_item_name,
        source_vendor_sku=line.source_vendor_sku,
        quantity=line.quantity,
        unit=line.unit,
        unit_price_snapshot=line.unit_price_snapshot,
        item_id=line.item_id,
        item_vendor_info_id=line.item_vendor_info_id,
        item_name_snapshot=line.item_name_snapshot,
        vendor_sku_snapshot=line.vendor_sku_snapshot,
        moved_to_order_id=line.moved_to_order_id,
        notes=line.notes,
        created_at=line.created_at,
        updated_at=line.updated_at,
    )


def _http_error_from_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)

    if "not found" in message.casefold():
        return HTTPException(status_code=404, detail=message)

    if "cannot" in message.casefold():
        return HTTPException(status_code=400, detail=message)

    if "required" in message.casefold():
        return HTTPException(status_code=400, detail=message)

    if "empty" in message.casefold():
        return HTTPException(status_code=400, detail=message)

    return HTTPException(status_code=400, detail=message)