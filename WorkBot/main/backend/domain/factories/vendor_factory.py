from __future__ import annotations

from typing import Optional

from backend.core.normalization.ids import IdGenerator
from backend.domain.models import (
    Vendor,
    OrderingInfo,
    ContactInfo,
)


class VendorFactory:
    def __init__(self, vendor_id_registry):
        self._vendor_id_registry = vendor_id_registry

    def create(
        self,
        *,
        name: str,
        order_format: str = '',
        special_notes: str = '',
        min_order_value: float = 0,
        min_order_cases: int = 0,
        internal_contacts: Optional[list[ContactInfo]] = None,
        ordering: Optional[OrderingInfo] = None,
        store_ids: Optional[dict[str, str]] = None,
    ) -> Vendor:
        name = name.strip()

        if not name:
            raise ValueError("Vendor name cannot be empty.")
        if min_order_value < 0:
            raise ValueError("min_order_value cannot be negative.")
        if min_order_cases < 0:
            raise ValueError("min_order_cases cannot be negative.")

        vendor_id = IdGenerator.unique_vendor_id(
            exists=self._vendor_id_registry.exists
        )

        return Vendor(
            id=vendor_id,
            name=name,
            order_format=order_format,
            special_notes=special_notes,
            min_order_value=min_order_value,
            min_order_cases=min_order_cases,
            internal_contacts=list(internal_contacts or []),
            ordering=ordering or OrderingInfo(),
            store_ids=dict(store_ids or {}),
        )