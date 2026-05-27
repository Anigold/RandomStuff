from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from apps.api.schemas.order_schema import (
    OrderDetailResponse,
    OrderLineResponse,
    OrderListResponse,
)
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
    orders = SqlOrderRepository(session)
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    store_obj = stores.get_by_name(store) if store else None
    vendor_obj = vendors.get_by_name(vendor) if vendor else None

    if store and store_obj is None:
        raise HTTPException(status_code=404, detail=f"Store not found: {store}")

    if vendor and vendor_obj is None:
        raise HTTPException(status_code=404, detail=f"Vendor not found: {vendor}")

    if store_obj and vendor_obj:
        order_list = orders.list_by_store_and_vendor(
            store_obj.id,
            vendor_obj.id,
            start_date=start_date,
            end_date=end_date,
        )
    elif store_obj:
        order_list = orders.list_by_store(
            store_obj.id,
            start_date=start_date,
            end_date=end_date,
        )
    elif vendor_obj:
        order_list = orders.list_by_vendor(
            vendor_obj.id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        order_list = orders.list_all()

    stores_by_id = {store.id: store for store in stores.list_all()}
    vendors_by_id = {vendor.id: vendor for vendor in vendors.list_all()}

    return [
        OrderListResponse(
            id=order.id,
            store_id=order.store_id,
            store_name=stores_by_id.get(order.store_id).name
            if order.store_id in stores_by_id
            else None,
            vendor_id=order.vendor_id,
            vendor_name=vendors_by_id.get(order.vendor_id).name
            if order.vendor_id in vendors_by_id
            else None,
            order_date=order.order_date,
            delivery_date=order.delivery_date,
            status=order.status.value,
            source=order.source,
            source_reference=order.source_reference,
            line_count=len(order.lines),
        )
        for order in order_list
    ]


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    session: Session = Depends(get_db_session),
) -> OrderDetailResponse:
    orders = SqlOrderRepository(session)
    stores = SqlStoreRepository(session)
    vendors = SqlVendorRepository(session)

    order = orders.get_by_id(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail=f"Order not found: {order_id}")

    store = stores.get_by_id(order.store_id)
    vendor = vendors.get_by_id(order.vendor_id)

    return OrderDetailResponse(
        id=order.id,
        store_id=order.store_id,
        store_name=store.name if store else None,
        vendor_id=order.vendor_id,
        vendor_name=vendor.name if vendor else None,
        order_date=order.order_date,
        delivery_date=order.delivery_date,
        status=order.status.value,
        source=order.source,
        source_reference=order.source_reference,
        line_count=len(order.lines),
        notes=order.notes,
        lines=[
            OrderLineResponse(
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
            for line in order.lines
        ],
    )