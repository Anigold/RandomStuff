from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from workbot_core.application.dto.item_import_row import (
    ItemImportRow,
    ItemStoreInfoImportRow,
    ItemVendorInfoImportRow,
)
from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.utils.ids import IdGenerator


class ItemImportService:
    """Creates replacement domain objects from item import rows.

    The domain models remain passive. This service decides what new objects
    should exist based on imported data.
    """

    def create_item(self, row: ItemImportRow) -> Item:
        return Item(
            id=row.id,
            name=self._required_text(row.name, "item name"),
            category=self._clean_optional(row.category),
            subcategory=self._clean_optional(row.subcategory),
            count_unit=self._clean_optional(row.count_unit),
            is_active=row.is_active,
        )

    def replace_item(self, existing: Item, row: ItemImportRow) -> Item:
        return replace(
            existing,
            name=self._required_text(row.name, "item name"),
            category=self._clean_optional(row.category),
            subcategory=self._clean_optional(row.subcategory),
            count_unit=self._clean_optional(row.count_unit),
            is_active=row.is_active,
        )

    def create_item_vendor_info(
        self,
        *,
        item_id: str,
        row: ItemVendorInfoImportRow,
    ) -> ItemVendorInfo:
        return ItemVendorInfo(
            id=IdGenerator.item_vendor_info_id(),
            item_id=item_id,
            vendor_id=row.vendor_id,
            vendor_sku=self._clean_optional(row.vendor_sku),
            purchase_unit=self._clean_optional(row.purchase_unit),
            pack_size=row.pack_size,
            price=row.price,
        )

    def replace_item_vendor_info(
        self,
        *,
        existing: ItemVendorInfo,
        row: ItemVendorInfoImportRow,
    ) -> ItemVendorInfo:
        return replace(
            existing,
            vendor_sku=self._clean_optional(row.vendor_sku),
            purchase_unit=self._clean_optional(row.purchase_unit),
            pack_size=row.pack_size,
            price=row.price,
        )

    def create_item_store_info(
        self,
        *,
        item_id: str,
        row: ItemStoreInfoImportRow,
    ) -> ItemStoreInfo:
        return ItemStoreInfo(
            id=IdGenerator.item_store_info_id(),
            item_id=item_id,
            store_id=row.store_id,
            count_unit=self._clean_optional(row.count_unit),
            par=row.par,
        )

    def replace_item_store_info(
        self,
        *,
        existing: ItemStoreInfo,
        row: ItemStoreInfoImportRow,
    ) -> ItemStoreInfo:
        return replace(
            existing,
            count_unit=self._clean_optional(row.count_unit),
            par=row.par,
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

    @staticmethod
    def normalize_decimal(value: object) -> Decimal | None:
        if value is None or value == "":
            return None

        return Decimal(str(value))