from __future__ import annotations

from typing import Any, Iterable

from backend.domain.models import Item, VendorItemInfo, StoreItemInfo


class ItemFactory:
    """
    Factory responsible for creating valid Item domain objects.

    Handles:
    - normalization
    - nested object creation
    - defensive defaults
    """

    @classmethod
    def create(
        cls,
        *,
        id: str,
        name: str,
        count_unit: str,
        category: str | None = None,
        subcategory: str | None = None,
        vendor_info: Iterable[dict[str, Any]] | None = None,
        store_info: Iterable[dict[str, Any]] | None = None,
        is_active: bool = True,
        is_inventoried: bool = True,
        notes: str | None = None,
        aliases: Iterable[str] | str | None = None,
    ) -> Item:

        normalized_aliases = cls._normalize_aliases(aliases)

        vendor_objects = [
            cls._build_vendor_info(v)
            for v in (vendor_info or [])
        ]

        store_objects = [
            cls._build_store_info(s)
            for s in (store_info or [])
        ]

        return Item(
            id=id,
            name=name,
            count_unit=count_unit,
            category=category,
            subcategory=subcategory,
            vendor_info=vendor_objects,
            store_info=store_objects,
            is_active=is_active,
            is_inventoried=is_inventoried,
            notes=notes,
            aliases=normalized_aliases,
        )

    # ---------------------------------------------------------
    # Builders
    # ---------------------------------------------------------

    @staticmethod
    def _build_vendor_info(data: dict[str, Any]) -> VendorItemInfo:
        return VendorItemInfo(
            vendor=data.get("vendor"),
            sku=data.get("sku"),
            unit=data.get("unit"),
            quantity=data.get("quantity"),
            cost=data.get("cost"),
        )

    @staticmethod
    def _build_store_info(data: dict[str, Any]) -> StoreItemInfo:
        try:
            return StoreItemInfo(
                store=data.get("store"),
                quantity_on_hand=data.get("quantity_on_hand"),
            )
        except TypeError:
            # In case StoreItemInfo does not include "store"
            return StoreItemInfo(
                quantity_on_hand=data.get("quantity_on_hand"),
            )

    # ---------------------------------------------------------
    # Normalization helpers
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_aliases(value: Iterable[str] | str | None) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            return [
                v.strip()
                for v in value.split(",")
                if v.strip()
            ]

        return [
            str(v).strip()
            for v in value
            if str(v).strip()
        ]