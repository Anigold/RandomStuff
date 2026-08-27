from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class ItemWritePayload:
    name: str

    category: str | None = None
    subcategory: str | None = None

    count_unit_quantity: Decimal | str | None = None
    count_unit_measure: str | None = None

    custom_each_name: str | None = None

    each_quantity: Decimal | str | None = None
    each_measure: str | None = None

    weight_quantity: Decimal | str | None = None
    weight_measure: str | None = None

    volume_quantity: Decimal | str | None = None
    volume_measure: str | None = None

    is_active: bool = True

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ItemWritePayload":
        return cls(
            name=data["name"],
            category=data.get("category"),
            subcategory=data.get("subcategory"),
            count_unit_quantity=data.get(
                "count_unit_quantity"
            ),
            count_unit_measure=data.get(
                "count_unit_measure"
            ),
            custom_each_name=data.get(
                "custom_each_name"
            ),
            each_quantity=data.get(
                "each_quantity"
            ),
            each_measure=data.get(
                "each_measure"
            ),
            weight_quantity=data.get(
                "weight_quantity"
            ),
            weight_measure=data.get(
                "weight_measure"
            ),
            volume_quantity=data.get(
                "volume_quantity"
            ),
            volume_measure=data.get(
                "volume_measure"
            ),
            is_active=data.get(
                "is_active",
                True,
            ),
        )

    @classmethod
    def from_item_detail(
        cls,
        detail: dict[str, Any],
    ) -> "ItemWritePayload":
        return cls.from_dict(detail)

    def with_updates(
        self,
        **changes: Any,
    ) -> "ItemWritePayload":
        values = self.to_dict()
        values.update(changes)

        return ItemWritePayload.from_dict(
            values
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "count_unit_quantity": self.count_unit_quantity,
            "count_unit_measure": self.count_unit_measure,
            "custom_each_name": self.custom_each_name,
            "each_quantity": self.each_quantity,
            "each_measure": self.each_measure,
            "weight_quantity": self.weight_quantity,
            "weight_measure": self.weight_measure,
            "volume_quantity": self.volume_quantity,
            "volume_measure": self.volume_measure,
            "is_active": self.is_active,
        }


@dataclass(slots=True)
class ItemStoreInfoWritePayload:
    store_id: str

    count_unit: str | None = None
    par: Decimal | str | None = None

    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "store_id": self.store_id,
            "count_unit": self.count_unit,
            "par": self.par,
            "is_active": self.is_active,
        }

@dataclass(slots=True)
class ItemStoreInfoUpdatePayload:
    count_unit: str | None = None
    par: Decimal | str | None = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "count_unit": self.count_unit,
            "par": self.par,
            "is_active": self.is_active,
        }