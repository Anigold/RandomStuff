from __future__ import annotations

from dataclasses import replace

from workbot_core.application.dto.item_catalog_commands import (
    UpdateItemVendorInfoCommand,
)
from workbot_core.application.interfaces.repositories import ItemVendorInfoRepository
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo


class ManageItemVendorInformation:
    def __init__(
        self,
        *,
        item_vendor_infos: ItemVendorInfoRepository,
    ) -> None:
        self._item_vendor_infos = item_vendor_infos

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