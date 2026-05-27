from __future__ import annotations

from workbot_core.application.dto.item_catalog_commands import (
    AddItemStoreInfoCommand,
    AddItemVendorInfoCommand,
    CreateItemCommand,
)
from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.utils.ids import IdGenerator


class ItemCatalogService:
    """Creates item catalog domain objects from validated command DTOs."""

    def create_item(self, command: CreateItemCommand) -> Item:
        return Item(
            id=IdGenerator.item_id(),
            name=self._required_text(command.name, "item name"),
            category=self._clean_optional(command.category),
            subcategory=self._clean_optional(command.subcategory),
            count_unit_quantity=command.count_unit_quantity,
            count_unit_measure=self._clean_optional(command.count_unit_measure),
            custom_each_name=self._clean_optional(command.custom_each_name),
            each_quantity=command.each_quantity,
            each_measure=self._clean_optional(command.each_measure),
            weight_quantity=command.weight_quantity,
            weight_measure=self._clean_optional(command.weight_measure),
            volume_quantity=command.volume_quantity,
            volume_measure=self._clean_optional(command.volume_measure),
            is_active=command.is_active,
        )

    def create_item_vendor_info(
        self,
        command: AddItemVendorInfoCommand,
    ) -> ItemVendorInfo:
        return ItemVendorInfo(
            id=IdGenerator.item_vendor_info_id(),
            item_id=command.item_id,
            vendor_id=command.vendor_id,
            vendor_sku=self._clean_optional(command.vendor_sku),
            purchase_unit=self._clean_optional(command.purchase_unit),
            pack_size=command.pack_size,
            price=command.price,
            is_active=command.is_active,
        )

    def create_item_store_info(
        self,
        command: AddItemStoreInfoCommand,
    ) -> ItemStoreInfo:
        return ItemStoreInfo(
            id=IdGenerator.item_store_info_id(),
            item_id=command.item_id,
            store_id=command.store_id,
            count_unit=self._clean_optional(command.count_unit),
            par=command.par,
            is_active=command.is_active,
        )

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        return cleaned or None

    @classmethod
    def _required_text(cls, value: str, field_name: str) -> str:
        cleaned = cls._clean_optional(value)

        if cleaned is None:
            raise ValueError(f"{field_name} cannot be empty.")

        return cleaned