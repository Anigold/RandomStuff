from __future__ import annotations

from decimal import Decimal

import pytest

from workbot_core.application.dto.item_catalog_commands import (
    CreateItemCommand,
    UpdateItemCommand,
)
from workbot_core.application.interfaces.repositories import ItemRepository
from workbot_core.application.use_cases.items.manage_items import ManageItems
from workbot_core.domain.models.item import Item


class FakeItemRepository(ItemRepository):
    def __init__(self, items: list[Item] | None = None) -> None:
        self._items: dict[str, Item] = {}

        for item in items or []:
            self._items[item.id] = item

    def save(self, item: Item) -> None:
        self._items[item.id] = item

    def get_by_id(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def get_by_name(self, name: str) -> Item | None:
        normalized = name.casefold().strip()

        for item in self._items.values():
            if item.name.casefold().strip() == normalized:
                return item

        return None

    def list_all(self) -> list[Item]:
        return list(self._items.values())

    def list_active(self) -> list[Item]:
        return [
            item
            for item in self._items.values()
            if item.is_active
        ]


def test_create_item_saves_new_item() -> None:
    items = FakeItemRepository()
    use_case = ManageItems(items=items)

    item = use_case.create_item(
        CreateItemCommand(
            name="Malt Barrel",
            category="Dry Goods",
            subcategory="B&B Ingredients",
            count_unit_quantity=Decimal("360.000"),
            count_unit_measure="lb",
            weight_quantity=Decimal("360.000"),
            weight_measure="lb",
            volume_quantity=Decimal("30.000"),
            volume_measure="gal",
        )
    )

    saved = items.get_by_id(item.id)

    assert saved is not None
    assert saved.id == item.id
    assert saved.name == "Malt Barrel"
    assert saved.category == "Dry Goods"
    assert saved.subcategory == "B&B Ingredients"
    assert saved.count_unit_quantity == Decimal("360.000")
    assert saved.count_unit_measure == "lb"
    assert saved.weight_quantity == Decimal("360.000")
    assert saved.weight_measure == "lb"
    assert saved.volume_quantity == Decimal("30.000")
    assert saved.volume_measure == "gal"
    assert saved.is_active is True


def test_create_item_rejects_duplicate_name() -> None:
    existing = _item(
        id="itm_existing",
        name="Malt Barrel",
    )

    items = FakeItemRepository([existing])
    use_case = ManageItems(items=items)

    with pytest.raises(ValueError, match="Item already exists: Malt Barrel"):
        use_case.create_item(
            CreateItemCommand(
                name="Malt Barrel",
            )
        )


def test_create_item_rejects_duplicate_name_case_insensitive() -> None:
    existing = _item(
        id="itm_existing",
        name="Malt Barrel",
    )

    items = FakeItemRepository([existing])
    use_case = ManageItems(items=items)

    with pytest.raises(ValueError, match="Item already exists: malt barrel"):
        use_case.create_item(
            CreateItemCommand(
                name="malt barrel",
            )
        )


def test_list_items_returns_all_items_by_default() -> None:
    active = _item(
        id="itm_active",
        name="Active Item",
        is_active=True,
    )
    inactive = _item(
        id="itm_inactive",
        name="Inactive Item",
        is_active=False,
    )

    use_case = ManageItems(
        items=FakeItemRepository([active, inactive]),
    )

    result = use_case.list_items()

    assert result == [active, inactive]


def test_list_items_can_exclude_inactive_items() -> None:
    active = _item(
        id="itm_active",
        name="Active Item",
        is_active=True,
    )
    inactive = _item(
        id="itm_inactive",
        name="Inactive Item",
        is_active=False,
    )

    use_case = ManageItems(
        items=FakeItemRepository([active, inactive]),
    )

    result = use_case.list_items(include_inactive=False)

    assert result == [active]


def test_list_items_can_search_by_name() -> None:
    malt_barrel = _item(
        id="itm_malt_barrel",
        name="Malt Barrel",
    )
    flour_bag = _item(
        id="itm_flour_bag",
        name="Flour Bag",
    )

    use_case = ManageItems(
        items=FakeItemRepository([malt_barrel, flour_bag]),
    )

    result = use_case.list_items(search="malt")

    assert result == [malt_barrel]


def test_get_item_returns_existing_item() -> None:
    item = _item(
        id="itm_existing",
        name="Malt Barrel",
    )

    use_case = ManageItems(
        items=FakeItemRepository([item]),
    )

    result = use_case.get_item("itm_existing")

    assert result == item


def test_get_item_rejects_missing_item() -> None:
    use_case = ManageItems(
        items=FakeItemRepository(),
    )

    with pytest.raises(ValueError, match="Item not found: itm_missing"):
        use_case.get_item("itm_missing")


def test_update_item_saves_updated_item() -> None:
    item = _item(
        id="itm_existing",
        name="Malt Barrel",
        category="Dry Goods",
        subcategory="Old Subcategory",
    )

    items = FakeItemRepository([item])
    use_case = ManageItems(items=items)

    updated = use_case.update_item(
        UpdateItemCommand(
            item_id="itm_existing",
            name="Malt Barrel Updated",
            category="Dry Goods",
            subcategory="B&B Ingredients",
            count_unit_quantity=Decimal("360.000"),
            count_unit_measure="lb",
            weight_quantity=Decimal("360.000"),
            weight_measure="lb",
            volume_quantity=Decimal("30.000"),
            volume_measure="gal",
            is_active=True,
        )
    )

    saved = items.get_by_id("itm_existing")

    assert saved == updated
    assert updated.id == "itm_existing"
    assert updated.name == "Malt Barrel Updated"
    assert updated.category == "Dry Goods"
    assert updated.subcategory == "B&B Ingredients"
    assert updated.count_unit_quantity == Decimal("360.000")
    assert updated.count_unit_measure == "lb"
    assert updated.weight_quantity == Decimal("360.000")
    assert updated.weight_measure == "lb"
    assert updated.volume_quantity == Decimal("30.000")
    assert updated.volume_measure == "gal"
    assert updated.is_active is True


def test_update_item_rejects_missing_item() -> None:
    use_case = ManageItems(
        items=FakeItemRepository(),
    )

    with pytest.raises(ValueError, match="Item not found: itm_missing"):
        use_case.update_item(
            UpdateItemCommand(
                item_id="itm_missing",
                name="Missing Item",
            )
        )


def test_update_item_rejects_duplicate_name_from_another_item() -> None:
    original = _item(
        id="itm_original",
        name="Original Item",
    )
    duplicate = _item(
        id="itm_duplicate",
        name="Duplicate Item",
    )

    use_case = ManageItems(
        items=FakeItemRepository([original, duplicate]),
    )

    with pytest.raises(ValueError, match="Item already exists: Duplicate Item"):
        use_case.update_item(
            UpdateItemCommand(
                item_id="itm_original",
                name="Duplicate Item",
            )
        )


def test_update_item_allows_keeping_same_name() -> None:
    item = _item(
        id="itm_existing",
        name="Malt Barrel",
    )

    items = FakeItemRepository([item])
    use_case = ManageItems(items=items)

    updated = use_case.update_item(
        UpdateItemCommand(
            item_id="itm_existing",
            name="Malt Barrel",
            category="Dry Goods",
            is_active=True,
        )
    )

    assert updated.id == "itm_existing"
    assert updated.name == "Malt Barrel"
    assert updated.category == "Dry Goods"


def test_deactivate_item_sets_is_active_false() -> None:
    item = _item(
        id="itm_existing",
        name="Malt Barrel",
        is_active=True,
    )

    items = FakeItemRepository([item])
    use_case = ManageItems(items=items)

    deactivated = use_case.deactivate_item("itm_existing")

    saved = items.get_by_id("itm_existing")

    assert saved == deactivated
    assert deactivated.id == "itm_existing"
    assert deactivated.is_active is False


def test_deactivate_item_rejects_missing_item() -> None:
    use_case = ManageItems(
        items=FakeItemRepository(),
    )

    with pytest.raises(ValueError, match="Item not found: itm_missing"):
        use_case.deactivate_item("itm_missing")


def _item(
    *,
    id: str,
    name: str,
    category: str | None = None,
    subcategory: str | None = None,
    count_unit_quantity: Decimal | None = None,
    count_unit_measure: str | None = None,
    custom_each_name: str | None = None,
    each_quantity: Decimal | None = None,
    each_measure: str | None = None,
    weight_quantity: Decimal | None = None,
    weight_measure: str | None = None,
    volume_quantity: Decimal | None = None,
    volume_measure: str | None = None,
    is_active: bool = True,
) -> Item:
    return Item(
        id=id,
        name=name,
        category=category,
        subcategory=subcategory,
        count_unit_quantity=count_unit_quantity,
        count_unit_measure=count_unit_measure,
        custom_each_name=custom_each_name,
        each_quantity=each_quantity,
        each_measure=each_measure,
        weight_quantity=weight_quantity,
        weight_measure=weight_measure,
        volume_quantity=volume_quantity,
        volume_measure=volume_measure,
        is_active=is_active,
    )