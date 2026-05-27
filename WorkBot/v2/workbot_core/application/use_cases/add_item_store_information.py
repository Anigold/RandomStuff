from __future__ import annotations

from workbot_core.application.dto.item_catalog_commands import AddItemStoreInfoCommand
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemStoreInfoRepository,
    StoreRepository,
)
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item_store_info import ItemStoreInfo


class AddItemStoreInfo:
    def __init__(
        self,
        *,
        items: ItemRepository,
        stores: StoreRepository,
        item_store_infos: ItemStoreInfoRepository,
        item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._stores = stores
        self._item_store_infos = item_store_infos
        self._service = item_catalog_service or ItemCatalogService()

    def run(self, command: AddItemStoreInfoCommand) -> ItemStoreInfo:
        item = self._items.get_by_id(command.item_id)

        if item is None:
            raise ValueError(f"Item not found: {command.item_id}")

        store = self._stores.get_by_id(command.store_id)

        if store is None:
            raise ValueError(f"Store not found: {command.store_id}")

        existing = self._item_store_infos.get_by_item_store(
            item_id=command.item_id,
            store_id=command.store_id,
        )

        if existing is not None:
            raise ValueError(
                "Item store info already exists: "
                f"item_id={command.item_id}, "
                f"store_id={command.store_id}"
            )

        info = self._service.create_item_store_info(command)
        self._item_store_infos.save(info)

        return info