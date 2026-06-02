# workbot_core/application/use_cases/manage_item_vendor_information.py

from __future__ import annotations

from dataclasses import replace

from workbot_core.application.dto.item_catalog_commands import (
    AddItemVendorInfoCommand,
    UpdateItemVendorInfoCommand,
)
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemVendorInfoRepository,
    VendorRepository,
)
from workbot_core.application.services.item_catalog_service import ItemCatalogService
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo


class ManageItemVendorInformation:
    def __init__(
        self,
        *,
        items: ItemRepository | None = None,
        vendors: VendorRepository | None = None,
        item_vendor_infos: ItemVendorInfoRepository,
        item_catalog_service: ItemCatalogService | None = None,
    ) -> None:
        self._items = items
        self._vendors = vendors
        self._item_vendor_infos = item_vendor_infos
        self._service = item_catalog_service or ItemCatalogService()

    def add_vendor_info(
        self,
        command: AddItemVendorInfoCommand,
    ) -> ItemVendorInfo:
        if self._items is None:
            raise ValueError("Item repository is required to add item vendor info.")

        if self._vendors is None:
            raise ValueError("Vendor repository is required to add item vendor info.")

        item = self._items.get_by_id(command.item_id)

        if item is None:
            raise ValueError(f"Item not found: {command.item_id}")

        vendor = self._vendors.get_by_id(command.vendor_id)

        if vendor is None:
            raise ValueError(f"Vendor not found: {command.vendor_id}")

        info = self._service.create_item_vendor_info(command)

        self._item_vendor_infos.save(info)

        return info

    def update_vendor_info(
        self,
        command: UpdateItemVendorInfoCommand,
    ) -> ItemVendorInfo:
        info = self._item_vendor_infos.get_by_id(command.info_id)

        if info is None or info.item_id != command.item_id:
            raise ValueError(f"Item vendor info not found: {command.info_id}")

        updated = replace(
            info,
            vendor_sku=self._clean_optional(command.vendor_sku),
            purchase_unit=self._clean_optional(command.purchase_unit),
            pack_size=command.pack_size,
            price=command.price,
            is_active=command.is_active,
        )

        self._item_vendor_infos.save(updated)

        return updated

    def deactivate_vendor_info(
        self,
        *,
        item_id: str,
        info_id: str,
    ) -> ItemVendorInfo:
        info = self._item_vendor_infos.get_by_id(info_id)

        if info is None or info.item_id != item_id:
            raise ValueError(f"Item vendor info not found: {info_id}")

        updated = replace(
            info,
            is_active=False,
        )

        self._item_vendor_infos.save(updated)

        return updated

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        return cleaned or None