from __future__ import annotations

from datetime import datetime

import pytest

from workbot_core.application.dto.store_commands import (
    CreateStoreCommand,
    UpdateStoreCommand,
)
from workbot_core.application.interfaces.repositories import StoreRepository
from workbot_core.application.use_cases.stores.manage_stores import ManageStores
from workbot_core.domain.models.store import Store


class FakeStoreRepository(StoreRepository):
    def __init__(self, stores: list[Store] | None = None) -> None:
        self._stores: dict[str, Store] = {}

        for store in stores or []:
            self._stores[store.id] = store

    def save(self, store: Store) -> None:
        self._stores[store.id] = store

    def get_by_id(self, store_id: str) -> Store | None:
        return self._stores.get(store_id)

    def get_by_name(self, name: str) -> Store | None:
        normalized = name.casefold().strip()

        for store in self._stores.values():
            if store.name.casefold().strip() == normalized:
                return store

        return None

    def list_all(self) -> list[Store]:
        return list(self._stores.values())

    def list_active(self) -> list[Store]:
        return [
            store
            for store in self._stores.values()
            if store.is_active
        ]


def test_create_store_saves_new_store() -> None:
    stores = FakeStoreRepository()
    use_case = ManageStores(stores=stores)

    store = use_case.create_store(
        CreateStoreCommand(
            name="Ithaca Bakery",
            general_manager="Andrew",
            inventory_clerk="Taylor",
            address="123 Bakery Lane",
            phone_number="555-123-4567",
            special_notes="Main production store",
        )
    )

    saved = stores.get_by_id(store.id)

    assert saved is not None
    assert saved.id == store.id
    assert saved.name == "Ithaca Bakery"
    assert saved.general_manager == "Andrew"
    assert saved.inventory_clerk == "Taylor"
    assert saved.address == "123 Bakery Lane"
    assert saved.phone_number == "555-123-4567"
    assert saved.special_notes == "Main production store"
    assert saved.is_active is True
    assert isinstance(saved.created_at, datetime)
    assert isinstance(saved.updated_at, datetime)


def test_create_store_cleans_optional_text_fields() -> None:
    stores = FakeStoreRepository()
    use_case = ManageStores(stores=stores)

    store = use_case.create_store(
        CreateStoreCommand(
            name="  Ithaca Bakery  ",
            general_manager="  Andrew  ",
            inventory_clerk="  ",
            address="  123 Bakery Lane  ",
            phone_number="  ",
            special_notes="  Notes  ",
        )
    )

    assert store.name == "Ithaca Bakery"
    assert store.general_manager == "Andrew"
    assert store.inventory_clerk is None
    assert store.address == "123 Bakery Lane"
    assert store.phone_number is None
    assert store.special_notes == "Notes"


def test_create_store_rejects_empty_name() -> None:
    use_case = ManageStores(stores=FakeStoreRepository())

    with pytest.raises(ValueError, match="store name cannot be empty."):
        use_case.create_store(
            CreateStoreCommand(
                name="   ",
            )
        )


def test_create_store_rejects_duplicate_name() -> None:
    existing = _store(
        id="sto_existing",
        name="Ithaca Bakery",
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([existing]),
    )

    with pytest.raises(ValueError, match="Store already exists: Ithaca Bakery"):
        use_case.create_store(
            CreateStoreCommand(
                name="Ithaca Bakery",
            )
        )


def test_create_store_rejects_duplicate_name_case_insensitive() -> None:
    existing = _store(
        id="sto_existing",
        name="Ithaca Bakery",
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([existing]),
    )

    with pytest.raises(ValueError, match="Store already exists: ithaca bakery"):
        use_case.create_store(
            CreateStoreCommand(
                name="ithaca bakery",
            )
        )


def test_list_stores_returns_all_stores_by_default() -> None:
    active = _store(
        id="sto_active",
        name="Active Store",
        is_active=True,
    )
    inactive = _store(
        id="sto_inactive",
        name="Inactive Store",
        is_active=False,
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([active, inactive]),
    )

    result = use_case.list_stores()

    assert result == [active, inactive]


def test_list_stores_can_exclude_inactive_stores() -> None:
    active = _store(
        id="sto_active",
        name="Active Store",
        is_active=True,
    )
    inactive = _store(
        id="sto_inactive",
        name="Inactive Store",
        is_active=False,
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([active, inactive]),
    )

    result = use_case.list_stores(include_inactive=False)

    assert result == [active]


def test_list_stores_can_search_by_name() -> None:
    ithaca = _store(
        id="sto_ithaca",
        name="Ithaca Bakery",
    )
    collegetown = _store(
        id="sto_collegetown",
        name="Collegetown Bagels",
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([ithaca, collegetown]),
    )

    result = use_case.list_stores(search="ithaca")

    assert result == [ithaca]


def test_get_store_returns_existing_store() -> None:
    store = _store(
        id="sto_existing",
        name="Ithaca Bakery",
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([store]),
    )

    result = use_case.get_store("sto_existing")

    assert result == store


def test_get_store_rejects_missing_store() -> None:
    use_case = ManageStores(
        stores=FakeStoreRepository(),
    )

    with pytest.raises(ValueError, match="Store not found: sto_missing"):
        use_case.get_store("sto_missing")


def test_update_store_saves_updated_store() -> None:
    store = _store(
        id="sto_existing",
        name="Ithaca Bakery",
        general_manager="Old Manager",
        inventory_clerk="Old Clerk",
        address="Old Address",
        phone_number="555-000-0000",
        special_notes="Old notes",
    )

    stores = FakeStoreRepository([store])
    use_case = ManageStores(stores=stores)

    updated = use_case.update_store(
        UpdateStoreCommand(
            store_id="sto_existing",
            name="Ithaca Bakery Updated",
            general_manager="Andrew",
            inventory_clerk="Taylor",
            address="123 Bakery Lane",
            phone_number="555-123-4567",
            special_notes="Updated notes",
            is_active=True,
        )
    )

    saved = stores.get_by_id("sto_existing")

    assert saved == updated
    assert updated.id == "sto_existing"
    assert updated.name == "Ithaca Bakery Updated"
    assert updated.general_manager == "Andrew"
    assert updated.inventory_clerk == "Taylor"
    assert updated.address == "123 Bakery Lane"
    assert updated.phone_number == "555-123-4567"
    assert updated.special_notes == "Updated notes"
    assert updated.is_active is True
    assert updated.created_at == store.created_at
    assert updated.updated_at != store.updated_at


def test_update_store_rejects_missing_store() -> None:
    use_case = ManageStores(
        stores=FakeStoreRepository(),
    )

    with pytest.raises(ValueError, match="Store not found: sto_missing"):
        use_case.update_store(
            UpdateStoreCommand(
                store_id="sto_missing",
                name="Missing Store",
            )
        )


def test_update_store_rejects_duplicate_name_from_another_store() -> None:
    original = _store(
        id="sto_original",
        name="Original Store",
    )
    duplicate = _store(
        id="sto_duplicate",
        name="Duplicate Store",
    )

    use_case = ManageStores(
        stores=FakeStoreRepository([original, duplicate]),
    )

    with pytest.raises(ValueError, match="Store already exists: Duplicate Store"):
        use_case.update_store(
            UpdateStoreCommand(
                store_id="sto_original",
                name="Duplicate Store",
            )
        )


def test_update_store_allows_keeping_same_name() -> None:
    store = _store(
        id="sto_existing",
        name="Ithaca Bakery",
    )

    stores = FakeStoreRepository([store])
    use_case = ManageStores(stores=stores)

    updated = use_case.update_store(
        UpdateStoreCommand(
            store_id="sto_existing",
            name="Ithaca Bakery",
            general_manager="Andrew",
            is_active=True,
        )
    )

    assert updated.id == "sto_existing"
    assert updated.name == "Ithaca Bakery"
    assert updated.general_manager == "Andrew"


def test_deactivate_store_sets_is_active_false() -> None:
    store = _store(
        id="sto_existing",
        name="Ithaca Bakery",
        is_active=True,
    )

    stores = FakeStoreRepository([store])
    use_case = ManageStores(stores=stores)

    deactivated = use_case.deactivate_store("sto_existing")

    saved = stores.get_by_id("sto_existing")

    assert saved == deactivated
    assert deactivated.id == "sto_existing"
    assert deactivated.is_active is False
    assert deactivated.created_at == store.created_at
    assert deactivated.updated_at != store.updated_at


def test_deactivate_store_rejects_missing_store() -> None:
    use_case = ManageStores(
        stores=FakeStoreRepository(),
    )

    with pytest.raises(ValueError, match="Store not found: sto_missing"):
        use_case.deactivate_store("sto_missing")


def _store(
    *,
    id: str,
    name: str,
    is_active: bool = True,
    general_manager: str | None = None,
    inventory_clerk: str | None = None,
    address: str | None = None,
    phone_number: str | None = None,
    special_notes: str = "",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> Store:
    created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    updated_at = updated_at or datetime(2026, 1, 1, 12, 0, 0)

    return Store(
        id=id,
        name=name,
        is_active=is_active,
        general_manager=general_manager,
        inventory_clerk=inventory_clerk,
        address=address,
        phone_number=phone_number,
        special_notes=special_notes,
        created_at=created_at,
        updated_at=updated_at,
    )