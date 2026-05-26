from __future__ import annotations

from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)



def test_store_repository_saves_and_loads_store(db_session):
    stores = SqlStoreRepository(db_session)

    store = Store(
        id="str_TEST",
        name="Bakery",
        general_manager="Test Manager",
        inventory_clerk="Test Clerk",
        address="123 Test St",
        phone_number="555-1234",
        special_notes="Test notes",
    )

    stores.save(store)
    db_session.commit()

    saved = stores.get_by_name("Bakery")

    assert saved is not None
    assert saved.id == "str_TEST"
    assert saved.name == "Bakery"
    assert saved.is_active is True
    assert saved.general_manager == "Test Manager"
    assert saved.inventory_clerk == "Test Clerk"
    assert saved.address == "123 Test St"
    assert saved.phone_number == "555-1234"
    assert saved.special_notes == "Test notes"


def test_store_repository_lists_active_stores(db_session):
    stores = SqlStoreRepository(db_session)

    stores.save(Store(id="str_ACTIVE", name="Active Store", is_active=True))
    stores.save(Store(id="str_INACTIVE", name="Inactive Store", is_active=False))
    db_session.commit()

    active_stores = stores.list_active()

    assert len(active_stores) == 1
    assert active_stores[0].id == "str_ACTIVE"