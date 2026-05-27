from __future__ import annotations

from workbot_core.application.dto.item_catalog_commands import CreateItemCommand
from workbot_core.application.interfaces.repositories import ItemRepository
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item import Item


class CreateItem:
    def __init__(
        self,
        *,
        items: ItemRepository,
        item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._service = item_catalog_service or ItemCatalogService()

    def run(self, command: CreateItemCommand) -> Item:
        existing = self._items.get_by_name(command.name)

        if existing is not None:
            raise ValueError(f"Item already exists: {command.name}")

        item = self._service.create_item(command)
        self._items.save(item)

        return item