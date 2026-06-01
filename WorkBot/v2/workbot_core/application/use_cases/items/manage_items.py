from __future__ import annotations

from dataclasses import replace

from workbot_core.application.dto.item_catalog_commands import (
    CreateItemCommand,
    UpdateItemCommand,
)
from workbot_core.application.interfaces.repositories import ItemRepository
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item import Item


class ManageItems:

    def __init__(self, *, 
                 items: ItemRepository, 
                 item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._service = item_catalog_service or ItemCatalogService()

    def create_item(self, command: CreateItemCommand) -> Item:

        existing = self._items.get_by_name(command.name)

        if existing is not None:
            raise ValueError(f"Item already exists: {command.name}")

        item = self._service.create_item(command)
        self._items.save(item)

        return item

    def list_items(self, *, 
                   include_inactive: bool = True, 
                   search: str | None = None,
    ) -> list[Item]:
        
        if include_inactive:
            items = self._items.list_all()
        else:
            items = self._items.list_active()

        if search:
            normalized = search.casefold().strip()
            items = [
                item
                for item in items
                if normalized in item.name.casefold()
            ]

        return items

    def get_item(self, item_id: str) -> Item:

        item = self._items.get_by_id(item_id)

        if item is None:
            raise ValueError(f"Item not found: {item_id}")

        return item

    def update_item(self, command: UpdateItemCommand) -> Item:

        item = self._items.get_by_id(command.item_id)

        if item is None:
            raise ValueError(f"Item not found: {command.item_id}")

        existing = self._items.get_by_name(command.name)

        if existing is not None and existing.id != item.id:
            raise ValueError(f"Item already exists: {command.name}")

        updated = replace(
            item,
            name=command.name,
            category=command.category,
            subcategory=command.subcategory,
            count_unit_quantity=command.count_unit_quantity,
            count_unit_measure=command.count_unit_measure,
            custom_each_name=command.custom_each_name,
            each_quantity=command.each_quantity,
            each_measure=command.each_measure,
            weight_quantity=command.weight_quantity,
            weight_measure=command.weight_measure,
            volume_quantity=command.volume_quantity,
            volume_measure=command.volume_measure,
            is_active=command.is_active,
        )

        self._items.save(updated)

        return updated

    def deactivate_item(self, item_id: str) -> Item:
        
        item = self._items.get_by_id(item_id)

        if item is None:
            raise ValueError(f"Item not found: {item_id}")

        updated = replace(item, is_active=False)

        self._items.save(updated)

        return updated