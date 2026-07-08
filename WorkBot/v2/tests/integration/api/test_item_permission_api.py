from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.auth.dependencies import get_current_user
from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID
from apps.api.main import app
from tests.integration.api.conftest import ApiTestContext
from tests.helpers.auth_helpers import (
    make_manager_user,
    make_supervisor_user,
    make_user_store_access,
    make_viewer_user,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserStoreAccessRepository,
)

ITEMS_PATH  = "/api/items"
STORES_PATH = "/api/stores"

SUPERVISOR_SCOPE_PARAMS   = {"scope_id": SUPERVISOR_SCOPE_ID}
SUPERVISOR_SCOPE_REQUIRED = "Supervisor scope required."


def test_manager_can_list_items_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    assigned_item_id = _create_item(client, name="Malt Barrel")
    other_item_id = _create_item(client, name="Flour Bag")

    _add_item_store_info(
        client,
        item_id=assigned_item_id,
        store_id=assigned_store_id,
    )
    _add_item_store_info(
        client,
        item_id=other_item_id,
        store_id=other_store_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        ITEMS_PATH,
        params={
            "scope_id": assigned_store_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    names = {item["name"] for item in data}

    assert "Malt Barrel" in names
    assert "Flour Bag" not in names


def test_manager_cannot_list_items_for_unassigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        ITEMS_PATH,
        params={
            "scope_id": other_store_id,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User does not have access to this store."


def test_manager_can_get_assigned_store_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_item(client, name="Malt Barrel")

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=store_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        _item_detail_path(item_id),
        params={
            "scope_id": store_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "Malt Barrel"
    assert data["vendor_info"] == []
    assert len(data["store_info"]) == 1
    assert data["store_info"][0]["store_id"] == store_id


def test_manager_cannot_get_unassigned_store_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    other_store_id = _create_store(client, name="Collegetown Bagels")

    item_id = _create_item(client, name="Flour Bag")

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=other_store_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(
        _item_detail_path(item_id),
        params={
            "scope_id": assigned_store_id,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access item for selected operating scope."


def test_manager_cannot_create_item(
    api_context: ApiTestContext,
) -> None:
    manager = make_manager_user()
    _authenticate_as(manager)

    response = api_context.client.post(
        ITEMS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_update_item(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    item_id = _create_item(client, name="Malt Barrel")

    manager = make_manager_user()
    _authenticate_as(manager)

    response = client.put(
        _item_detail_path(item_id),
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Updated Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_delete_item(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    item_id = _create_item(client, name="Malt Barrel")

    manager = make_manager_user()
    _authenticate_as(manager)

    response = client.delete(
        _item_detail_path(item_id),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_viewer_can_get_assigned_store_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_item(client, name="Malt Barrel")

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=store_id,
    )

    viewer = make_viewer_user()
    _grant_store_access(
        api_context,
        user_id=viewer.id,
        store_id=store_id,
    )
    _authenticate_as(viewer)

    response = client.get(
        _item_detail_path(item_id),
        params={
            "scope_id": store_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_viewer_cannot_create_item(
    api_context: ApiTestContext,
) -> None:
    viewer = make_viewer_user()
    _authenticate_as(viewer)

    response = api_context.client.post(
        ITEMS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_supervisor_can_get_full_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_item(client, name="Malt Barrel")

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=store_id,
    )

    response = client.get(
        _item_detail_path(item_id),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert len(data["store_info"]) == 1


def _authenticate_as(user) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def _grant_store_access(
    api_context: ApiTestContext,
    *,
    user_id: str,
    store_id: str,
) -> None:
    access = make_user_store_access(
        user_id=user_id,
        store_id=store_id,
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


def _create_item(client: TestClient, *, name: str) -> str:
    response = client.post(
        ITEMS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": name,
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _add_item_store_info(
    client: TestClient,
    *,
    item_id: str,
    store_id: str,
) -> str:
    response = client.post(
        _item_store_info_collection_path(item_id),
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "store_id": store_id,
            "count_unit": "bag",
            "par": "6",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _item_detail_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}"


def _item_store_info_collection_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}/store-info"