from __future__ import annotations

from datetime import date

from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.domain.models.order import Order


class FakeItemRepository:
    def __init__(self, items: list[Item] | None = None) -> None:
        self._items: dict[str, Item] = {}

        for item in items or []:
            self._items[item.id] = item

    def save(self, item: Item) -> None:
        self._items[item.id] = item

    def get_by_id(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def get_by_name(self, name: str) -> Item | None:
        normalized = name.casefold().strip()

        for item in self._items.values():
            if item.name.casefold().strip() == normalized:
                return item

        return None

    def list_all(self) -> list[Item]:
        return list(self._items.values())

    def list_active(self) -> list[Item]:
        return [
            item
            for item in self._items.values()
            if item.is_active
        ]


class FakeStoreRepository:
    def __init__(self, stores: list[Store] | None = None) -> None:
        self._stores: dict[str, Store] = {}

        for store in stores or []:
            self._stores[store.id] = store

    def save(self, store: Store) -> None:
        self._stores[store.id] = store

    def get_by_id(self, store_id: str) -> Store | None:
        return self._stores.get(store_id)

    def get_by_name(self, name: str) -> Store | None:
        normalized = name.casefold().strip()

        for store in self._stores.values():
            if store.name.casefold().strip() == normalized:
                return store

        return None

    def list_all(self) -> list[Store]:
        return list(self._stores.values())

    def list_active(self) -> list[Store]:
        return [
            store
            for store in self._stores.values()
            if store.is_active
        ]


class FakeVendorRepository:
    def __init__(self, vendors: list[Vendor] | None = None) -> None:
        self._vendors: dict[str, Vendor] = {}

        for vendor in vendors or []:
            self._vendors[vendor.id] = vendor

    def save(self, vendor: Vendor) -> None:
        self._vendors[vendor.id] = vendor

    def get_by_id(self, vendor_id: str) -> Vendor | None:
        return self._vendors.get(vendor_id)

    def get_by_name(self, name: str) -> Vendor | None:
        normalized = name.casefold().strip()

        for vendor in self._vendors.values():
            if vendor.name.casefold().strip() == normalized:
                return vendor

        return None

    def list_all(self) -> list[Vendor]:
        return list(self._vendors.values())

    def list_active(self) -> list[Vendor]:
        return [
            vendor
            for vendor in self._vendors.values()
            if vendor.is_active
        ]


class FakeItemVendorInfoRepository:
    def __init__(
        self,
        infos: list[ItemVendorInfo] | None = None,
    ) -> None:
        self._infos: dict[str, ItemVendorInfo] = {}

        for info in infos or []:
            self._infos[info.id] = info

    def save(self, info: ItemVendorInfo) -> None:
        self._infos[info.id] = info

    def get_by_id(self, info_id: str) -> ItemVendorInfo | None:
        return self._infos.get(info_id)

    def list_for_item(self, item_id: str) -> list[ItemVendorInfo]:
        return [
            info
            for info in self._infos.values()
            if info.item_id == item_id
        ]

    def list_all(self) -> list[ItemVendorInfo]:
        return list(self._infos.values())

    def list_active(self) -> list[ItemVendorInfo]:
        return [
            info
            for info in self._infos.values()
            if info.is_active
        ]


class FakeItemStoreInfoRepository:
    def __init__(
        self,
        infos: list[ItemStoreInfo] | None = None,
    ) -> None:
        self._infos: dict[str, ItemStoreInfo] = {}

        for info in infos or []:
            self._infos[info.id] = info

    def save(self, info: ItemStoreInfo) -> None:
        self._infos[info.id] = info

    def get_by_id(self, info_id: str) -> ItemStoreInfo | None:
        return self._infos.get(info_id)

    def list_for_item(self, item_id: str) -> list[ItemStoreInfo]:
        return [
            info
            for info in self._infos.values()
            if info.item_id == item_id
        ]

    def list_all(self) -> list[ItemStoreInfo]:
        return list(self._infos.values())

    def list_active(self) -> list[ItemStoreInfo]:
        return [
            info
            for info in self._infos.values()
            if info.is_active
        ]
    
class FakeOrderRepository:
    def __init__(self, orders: list[Order] | None = None) -> None:
        self._orders: dict[str, Order] = {}

        for order in orders or []:
            self._orders[order.id] = order

    def save(self, order: Order) -> None:
        self._orders[order.id] = order

    def get_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def get_by_source_reference(
        self,
        *,
        store_id: str,
        vendor_id: str,
        order_date: date,
        source: str,
        source_reference: str,
    ) -> Order | None:
        for order in self._orders.values():
            if (
                order.store_id == store_id
                and order.vendor_id == vendor_id
                and order.order_date == order_date
                and order.source == source
                and order.source_reference == source_reference
            ):
                return order

        return None

    def list_all(self) -> list[Order]:
        return list(self._orders.values())

    def list_by_store(
        self,
        store_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        return [
            order
            for order in self._orders.values()
            if order.store_id == store_id
            and _date_is_in_range(
                order.order_date,
                start_date=start_date,
                end_date=end_date,
            )
        ]

    def list_by_vendor(
        self,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        return [
            order
            for order in self._orders.values()
            if order.vendor_id == vendor_id
            and _date_is_in_range(
                order.order_date,
                start_date=start_date,
                end_date=end_date,
            )
        ]

    def list_by_store_and_vendor(
        self,
        store_id: str,
        vendor_id: str,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        return [
            order
            for order in self._orders.values()
            if order.store_id == store_id
            and order.vendor_id == vendor_id
            and _date_is_in_range(
                order.order_date,
                start_date=start_date,
                end_date=end_date,
            )
        ]

    def delete(self, order_id: str) -> None:
        self._orders.pop(order_id, None)

def _date_is_in_range(
    value: date,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> bool:
    if start_date is not None and value < start_date:
        return False

    if end_date is not None and value > end_date:
        return False

    return True