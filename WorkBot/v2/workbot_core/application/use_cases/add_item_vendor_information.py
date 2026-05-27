from __future__ import annotations

from workbot_core.application.dto.item_catalog_commands import AddItemVendorInfoCommand
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemVendorInfoRepository,
    VendorRepository,
)
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo


class AddItemVendorInfo:
    def __init__(
        self,
        *,
        items: ItemRepository,
        vendors: VendorRepository,
        item_vendor_infos: ItemVendorInfoRepository,
        item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._vendors = vendors
        self._item_vendor_infos = item_vendor_infos
        self._service = item_catalog_service or ItemCatalogService()

    def run(self, command: AddItemVendorInfoCommand) -> ItemVendorInfo:
        item = self._items.get_by_id(command.item_id)

        if item is None:
            raise ValueError(f"Item not found: {command.item_id}")

        vendor = self._vendors.get_by_id(command.vendor_id)

        if vendor is None:
            raise ValueError(f"Vendor not found: {command.vendor_id}")

        existing = self._item_vendor_infos.get_by_item_vendor_sku(
            item_id=command.item_id,
            vendor_id=command.vendor_id,
            vendor_sku=command.vendor_sku,
        )

        if existing is not None:
            raise ValueError(
                "Item vendor info already exists: "
                f"item_id={command.item_id}, "
                f"vendor_id={command.vendor_id}, "
                f"vendor_sku={command.vendor_sku}"
            )

        info = self._service.create_item_vendor_info(command)
        self._item_vendor_infos.save(info)

        return info