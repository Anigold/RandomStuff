# workbot_core/application/use_cases/manage_item_store_information.py

from __future__ import annotations

from dataclasses import replace

from workbot_core.application.dto.item_catalog_commands import (
    AddItemStoreInfoCommand,
    UpdateItemStoreInfoCommand,
)
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemStoreInfoRepository,
    StoreRepository,
)
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item_store_info import ItemStoreInfo


class ManageItemStoreInformation:
    def __init__(
        self,
        *,
        items: ItemRepository | None = None,
        stores: StoreRepository | None = None,
        item_store_infos: ItemStoreInfoRepository,
        item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._stores = stores
        self._item_store_infos = item_store_infos
        self._service = item_catalog_service or ItemCatalogService()

    def add_store_info(
        self,
        command: AddItemStoreInfoCommand,
    ) -> ItemStoreInfo:
        if self._items is None:
            raise ValueError("Item repository is required to add item store info.")

        if self._stores is None:
            raise ValueError("Store repository is required to add item store info.")

        item = self._items.get_by_id(command.item_id)

        if item is None:
            raise ValueError(f"Item not found: {command.item_id}")

        store = self._stores.get_by_id(command.store_id)

        if store is None:
            raise ValueError(f"Store not found: {command.store_id}")

        info = self._service.create_item_store_info(command)

        self._item_store_infos.save(info)

        return info

    def update_store_info(
        self,
        command: UpdateItemStoreInfoCommand,
    ) -> ItemStoreInfo:
        info = self._item_store_infos.get_by_id(command.info_id)

        if info is None or info.item_id != command.item_id:
            raise ValueError(f"Item store info not found: {command.info_id}")

        updated = replace(
            info,
            count_unit=self._clean_optional(command.count_unit),
            par=command.par,
            is_active=command.is_active,
        )

        self._item_store_infos.save(updated)

        return updated

    def deactivate_store_info(
        self,
        *,
        item_id: str,
        info_id: str,
    ) -> ItemStoreInfo:
        info = self._item_store_infos.get_by_id(info_id)

        if info is None or info.item_id != item_id:
            raise ValueError(f"Item store info not found: {info_id}")

        updated = replace(
            info,
            is_active=False,
        )

        self._item_store_infos.save(updated)

        return updated

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        return cleaned or None