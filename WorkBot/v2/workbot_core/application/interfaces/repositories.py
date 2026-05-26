from __future__ import annotations

from typing import Protocol
from datetime import date

from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.domain.models import (
    ItemVendorInfo, 
    ItemStoreInfo, 
    Item,
    Order
)


class StoreRepository(Protocol):
    def get_by_id(self, store_id: str) -> Store | None: ...

    def get_by_name(self, name: str) -> Store | None: ...

    def list_all(self) -> list[Store]: ...

    def list_active(self) -> list[Store]: ...

    def save(self, store: Store) -> None: ...

    def delete(self, store_id: str) -> None: ...


class VendorRepository(Protocol):
    def get_by_id(self, vendor_id: str) -> Vendor | None: ...

    def get_by_name(self, name: str) -> Vendor | None: ...

    def list_all(self) -> list[Vendor]: ...

    def list_active(self) -> list[Vendor]: ...

    def save(self, vendor: Vendor) -> None: ...

    def delete(self, vendor_id: str) -> None: ...


class ItemRepository(Protocol):
    def get_by_id(self, item_id: str) -> Item | None: ...

    def get_by_name(self, name: str) -> Item | None: ...

    def list_all(self) -> list[Item]: ...

    def list_active(self) -> list[Item]: ...

    def save(self, item: Item) -> None: ...

    def delete(self, item_id: str) -> None: ...


class ItemVendorInfoRepository(Protocol):
    def get_by_id(self, info_id: str) -> ItemVendorInfo | None: ...

    def get_by_item_vendor_sku(
        self,
        *,
        item_id: str,
        vendor_id: str,
        vendor_sku: str | None,
    ) -> ItemVendorInfo | None: ...

    def list_for_item(self, item_id: str) -> list[ItemVendorInfo]: ...

    def list_for_vendor(self, vendor_id: str) -> list[ItemVendorInfo]: ...

    def list_active_for_vendor(self, vendor_id: str) -> list[ItemVendorInfo]: ...

    def save(self, info: ItemVendorInfo) -> None: ...

    def delete(self, info_id: str) -> None: ...


class ItemStoreInfoRepository(Protocol):
    def get_by_id(self, info_id: str) -> ItemStoreInfo | None: ...

    def get_by_item_store(
        self,
        *,
        item_id: str,
        store_id: str,
    ) -> ItemStoreInfo | None: ...

    def list_for_item(self, item_id: str) -> list[ItemStoreInfo]: ...

    def list_for_store(self, store_id: str) -> list[ItemStoreInfo]: ...

    def save(self, info: ItemStoreInfo) -> None: ...

    def delete(self, info_id: str) -> None: ...


class OrderRepository(Protocol):

    def get_by_id(self, order_id: str) -> Order | None: ...

    def list_all(self) -> list[Order]: ...

    def list_by_store(
        self,
        store_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]: ...

    def list_by_vendor(
        self,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]: ...

    def list_by_store_and_vendor(
        self,
        store_id: str,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]: ...

    def save(self, order: Order) -> None: ...

    def delete(self, order_id: str) -> None: ...