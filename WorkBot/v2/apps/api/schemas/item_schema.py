from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CreateItemRequest(BaseModel):
    name: str
    category: str | None = None
    subcategory: str | None = None

    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None

    custom_each_name: str | None = None

    each_quantity: Decimal | None = None
    each_measure: str | None = None

    weight_quantity: Decimal | None = None
    weight_measure: str | None = None

    volume_quantity: Decimal | None = None
    volume_measure: str | None = None

    is_active: bool = True


class ItemResponse(BaseModel):
    id: str
    name: str

    category: str | None = None
    subcategory: str | None = None

    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None

    custom_each_name: str | None = None

    each_quantity: Decimal | None = None
    each_measure: str | None = None

    weight_quantity: Decimal | None = None
    weight_measure: str | None = None

    volume_quantity: Decimal | None = None
    volume_measure: str | None = None

    is_active: bool

    created_at: datetime | None = None
    updated_at: datetime | None = None


class AddItemVendorInfoRequest(BaseModel):
    vendor_id: str

    vendor_sku: str | None = None
    purchase_unit: str | None = None
    pack_size: Decimal | None = None
    price: Decimal | None = None

    is_active: bool = True


class ItemVendorInfoResponse(BaseModel):
    id: str

    item_id: str
    vendor_id: str

    vendor_sku: str | None = None
    purchase_unit: str | None = None
    pack_size: Decimal | None = None
    price: Decimal | None = None

    last_purchase_date: datetime | None = None
    is_active: bool

    created_at: datetime | None = None
    updated_at: datetime | None = None


class AddItemStoreInfoRequest(BaseModel):
    store_id: str

    count_unit: str | None = None
    par: Decimal | None = None

    is_active: bool = True


class ItemStoreInfoResponse(BaseModel):
    id: str

    item_id: str
    store_id: str

    count_unit: str | None = None
    par: Decimal | None = None

    is_active: bool

    created_at: datetime | None = None
    updated_at: datetime | None = None


class ItemDetailResponse(ItemResponse):
    vendor_info: list[ItemVendorInfoResponse]
    store_info: list[ItemStoreInfoResponse]


class UpdateItemRequest(BaseModel):
    name: str
    category: str | None = None
    subcategory: str | None = None

    count_unit_quantity: Decimal | None = None
    count_unit_measure: str | None = None

    custom_each_name: str | None = None

    each_quantity: Decimal | None = None
    each_measure: str | None = None

    weight_quantity: Decimal | None = None
    weight_measure: str | None = None

    volume_quantity: Decimal | None = None
    volume_measure: str | None = None

    is_active: bool = True


class UpdateItemVendorInfoRequest(BaseModel):
    vendor_sku: str | None = None
    purchase_unit: str | None = None
    pack_size: Decimal | None = None
    price: Decimal | None = None
    is_active: bool = True


class UpdateItemStoreInfoRequest(BaseModel):
    count_unit: str | None = None
    par: Decimal | None = None
    is_active: bool = True