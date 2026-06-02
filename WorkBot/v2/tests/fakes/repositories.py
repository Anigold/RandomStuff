from __future__ import annotations

from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor


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