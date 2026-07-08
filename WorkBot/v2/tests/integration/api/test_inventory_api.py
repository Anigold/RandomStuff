from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from fastapi.testclient import TestClient

from apps.api.auth.dependencies import get_current_user
from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID
from apps.api.main import app
from tests.integration.api.conftest import ApiTestContext
from tests.helpers.auth_helpers import (
    make_manager_user,
    make_supervisor_user,
    make_user_store_access,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserStoreAccessRepository,
)

INVENTORY_PATH = "/api/inventory"
ITEMS_PATH = "/api/items"
STORES_PATH = "/api/stores"

SUPERVISOR_SCOPE_PARAMS = {"scope_id": SUPERVISOR_SCOPE_ID}
SINGLE_STORE_SCOPE_REQUIRED = "A single store scope is required for this operation."


def test_manager_can_list_inventory_items_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    malt_item_id = _create_item(
        client,
        name="Malt Barrel",
        category="Dry Goods",
        subcategory="B&B Ingredients",
        count_unit_quantity="360.000",
        count_unit_measure="lb",
    )
    flour_item_id = _create_item(
        client,
        name="Flour Bag",
        category="Dry Goods",
        subcategory="B&B Ingredients",
        count_unit_quantity="50.000",
        count_unit_measure="lb",
    )
    inactive_store_item_id = _create_item(
        client,
        name="Inactive Store Item",
        category="Dry Goods",
        subcategory="B&B Ingredients",
    )

    _add_item_store_info(
        client,
        item_id=malt_item_id,
        store_id=store_id,
        is_active=True,
    )
    _add_item_store_info(
        client,
        item_id=flour_item_id,
        store_id=other_store_id,
        is_active=True,
    )
    _add_item_store_info(
        client,
        item_id=inactive_store_item_id,
        store_id=store_id,
        is_active=False,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        _inventory_items_path(),
        params=_store_scope_params(store_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == malt_item_id
    assert data[0]["name"] == "Malt Barrel"
    assert data[0]["category"] == "Dry Goods"
    assert data[0]["subcategory"] == "B&B Ingredients"
    assert data[0]["count_unit_quantity"] == "360.000"
    assert data[0]["count_unit_measure"] == "lb"
    assert data[0]["is_active"] is True


def test_inventory_items_rejects_supervisor_scope(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    response = client.get(
        _inventory_items_path(),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == SINGLE_STORE_SCOPE_REQUIRED


def test_manager_can_create_inventory_count_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        _inventory_counts_path(),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-08",
            "notes": "Opening inventory count",
            "lines": [
                {
                    "item_id": item_id,
                    "quantity": "2",
                    "unit": "barrel",
                    "notes": "Back room",
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"].startswith("inc_")
    assert data["store_id"] == store_id
    assert data["count_date"] == "2026-07-08"
    assert data["status"] == "draft"
    assert data["notes"] == "Opening inventory count"
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    assert len(data["lines"]) == 1

    line = data["lines"][0]

    assert line["id"].startswith("icl_")
    assert line["inventory_count_id"] == data["id"]
    assert line["item_id"] == item_id
    assert line["item_name"] == "Malt Barrel"
    assert Decimal(line["quantity"]) == Decimal("2")
    assert line["unit"] == "barrel"
    assert line["notes"] == "Back room"
    assert line["created_at"] is not None
    assert line["updated_at"] is not None


def test_create_inventory_count_rejects_item_not_available_to_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    item_id = _create_inventory_available_item(
        client,
        store_id=other_store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        _inventory_counts_path(),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-08",
            "notes": None,
            "lines": [
                {
                    "item_id": item_id,
                    "quantity": "2",
                    "unit": "barrel",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Inventory count contains items not available to this store: "
        f"{item_id}"
    )


def test_manager_can_list_inventory_counts_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )
    other_item_id = _create_inventory_available_item(
        client,
        store_id=other_store_id,
        name="Flour Bag",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=other_store_id,
    )
    _authenticate_as(manager)

    included_count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )
    _create_inventory_count(
        client,
        store_id=other_store_id,
        item_id=other_item_id,
        count_date="2026-07-08",
    )

    response = client.get(
        _inventory_counts_path(),
        params=_store_scope_params(store_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == included_count_id
    assert data[0]["store_id"] == store_id
    assert data[0]["count_date"] == "2026-07-08"
    assert data[0]["status"] == "draft"


def test_manager_can_get_inventory_count_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )

    response = client.get(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(store_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == count_id
    assert data["store_id"] == store_id
    assert data["count_date"] == "2026-07-08"
    assert data["status"] == "draft"
    assert len(data["lines"]) == 1
    assert data["lines"][0]["item_id"] == item_id


def test_manager_cannot_get_inventory_count_for_another_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    item_id = _create_inventory_available_item(
        client,
        store_id=other_store_id,
        name="Malt Barrel",
    )

    setup_manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=setup_manager.id,
        store_id=other_store_id,
    )
    _authenticate_as(setup_manager)

    count_id = _create_inventory_count(
        client,
        store_id=other_store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(assigned_store_id),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access inventory count for another store."


def test_manager_can_update_draft_inventory_count_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    malt_item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )
    flour_item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Flour Bag",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=malt_item_id,
        count_date="2026-07-08",
    )

    response = client.put(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-09",
            "notes": "Updated draft count",
            "lines": [
                {
                    "item_id": malt_item_id,
                    "quantity": "3",
                    "unit": "barrel",
                    "notes": "Updated back room count",
                },
                {
                    "item_id": flour_item_id,
                    "quantity": "12",
                    "unit": "bag",
                    "notes": "Shelf count",
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == count_id
    assert data["store_id"] == store_id
    assert data["count_date"] == "2026-07-09"
    assert data["status"] == "draft"
    assert data["notes"] == "Updated draft count"
    assert len(data["lines"]) == 2

    lines_by_item_id = {
        line["item_id"]: line
        for line in data["lines"]
    }

    assert Decimal(lines_by_item_id[malt_item_id]["quantity"]) == Decimal("3")
    assert lines_by_item_id[malt_item_id]["unit"] == "barrel"
    assert lines_by_item_id[malt_item_id]["notes"] == "Updated back room count"

    assert Decimal(lines_by_item_id[flour_item_id]["quantity"]) == Decimal("12")
    assert lines_by_item_id[flour_item_id]["unit"] == "bag"
    assert lines_by_item_id[flour_item_id]["notes"] == "Shelf count"


def test_update_inventory_count_rejects_submitted_count(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )

    submit_response = client.post(
        _inventory_count_submit_path(count_id),
        params=_store_scope_params(store_id),
    )

    assert submit_response.status_code == 200

    response = client.put(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-09",
            "notes": "Should not update",
            "lines": [
                {
                    "item_id": item_id,
                    "quantity": "3",
                    "unit": "barrel",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Submitted inventory counts cannot be updated."


def test_update_inventory_count_rejects_item_not_available_to_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )
    other_item_id = _create_inventory_available_item(
        client,
        store_id=other_store_id,
        name="Flour Bag",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )

    response = client.put(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-09",
            "notes": "Invalid item update",
            "lines": [
                {
                    "item_id": other_item_id,
                    "quantity": "3",
                    "unit": "bag",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Inventory count contains items not available to this store: "
        f"{other_item_id}"
    )


def test_update_inventory_count_returns_404_for_missing_count(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.put(
        _inventory_count_detail_path("inc_missing"),
        params=_store_scope_params(store_id),
        json={
            "count_date": "2026-07-09",
            "notes": "Missing count",
            "lines": [
                {
                    "item_id": item_id,
                    "quantity": "3",
                    "unit": "barrel",
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory count not found."


def test_update_inventory_count_rejects_another_store_count(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    other_item_id = _create_inventory_available_item(
        client,
        store_id=other_store_id,
        name="Malt Barrel",
    )

    setup_manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=setup_manager.id,
        store_id=other_store_id,
    )
    _authenticate_as(setup_manager)

    count_id = _create_inventory_count(
        client,
        store_id=other_store_id,
        item_id=other_item_id,
        count_date="2026-07-08",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.put(
        _inventory_count_detail_path(count_id),
        params=_store_scope_params(assigned_store_id),
        json={
            "count_date": "2026-07-09",
            "notes": "Wrong store",
            "lines": [
                {
                    "item_id": other_item_id,
                    "quantity": "3",
                    "unit": "barrel",
                }
            ],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot update inventory count for another store."


def test_manager_can_submit_inventory_count_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_inventory_available_item(
        client,
        store_id=store_id,
        name="Malt Barrel",
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    count_id = _create_inventory_count(
        client,
        store_id=store_id,
        item_id=item_id,
        count_date="2026-07-08",
    )

    response = client.post(
        _inventory_count_submit_path(count_id),
        params=_store_scope_params(store_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == count_id
    assert data["store_id"] == store_id
    assert data["status"] == "submitted"


def test_submit_inventory_count_returns_404_for_missing_count(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        _inventory_count_submit_path("inc_missing"),
        params=_store_scope_params(store_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory count not found."


def test_inventory_counts_rejects_supervisor_scope(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    response = client.get(
        _inventory_counts_path(),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == SINGLE_STORE_SCOPE_REQUIRED


def _authenticate_as(user) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def _grant_store_access(
    api_context: ApiTestContext,
    *,
    user_id: str,
    store_id: str,
) -> None:
    access = replace(
        make_user_store_access(
            user_id=user_id,
            store_id=store_id,
        ),
        id=f"usa_{user_id}_{store_id}",
    )

    with api_context.session_factory() as session:
        SqlUserStoreAccessRepository(session).save(access)
        session.commit()


def _create_store(client: TestClient, *, name: str) -> str:
    response = client.post(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": name,
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _create_item(
    client: TestClient,
    *,
    name: str,
    category: str = "Dry Goods",
    subcategory: str | None = None,
    count_unit_quantity: str | None = None,
    count_unit_measure: str | None = None,
) -> str:
    response = client.post(
        ITEMS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": name,
            "category": category,
            "subcategory": subcategory,
            "count_unit_quantity": count_unit_quantity,
            "count_unit_measure": count_unit_measure,
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _create_inventory_available_item(
    client: TestClient,
    *,
    store_id: str,
    name: str,
) -> str:
    item_id = _create_item(
        client,
        name=name,
        category="Dry Goods",
        subcategory="B&B Ingredients",
        count_unit_quantity="360.000",
        count_unit_measure="lb",
    )

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=store_id,
        is_active=True,
    )

    return item_id


def _add_item_store_info(
    client: TestClient,
    *,
    item_id: str,
    store_id: str,
    is_active: bool,
) -> str:
    response = client.post(
        _item_store_info_collection_path(item_id),
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "store_id": store_id,
            "count_unit": "barrel",
            "par": "6",
            "is_active": is_active,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _create_inventory_count(
    client: TestClient,
    *,
    store_id: str,
    item_id: str,
    count_date: str,
) -> str:
    response = client.post(
        _inventory_counts_path(),
        params=_store_scope_params(store_id),
        json={
            "count_date": count_date,
            "notes": "Opening inventory count",
            "lines": [
                {
                    "item_id": item_id,
                    "quantity": "2",
                    "unit": "barrel",
                    "notes": "Back room",
                }
            ],
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _store_scope_params(store_id: str) -> dict[str, str]:
    return {
        "scope_id": store_id,
    }


def _inventory_items_path() -> str:
    return f"{INVENTORY_PATH}/items"


def _inventory_counts_path() -> str:
    return f"{INVENTORY_PATH}/counts"


def _inventory_count_detail_path(count_id: str) -> str:
    return f"{_inventory_counts_path()}/{count_id}"


def _inventory_count_submit_path(count_id: str) -> str:
    return f"{_inventory_count_detail_path(count_id)}/submit"


def _item_store_info_collection_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}/store-info"