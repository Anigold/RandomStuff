from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.auth.dependencies import get_current_user
from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID
from apps.api.main import app
from tests.integration.api.conftest import ApiTestContext
from tests.helpers.auth_helpers import (
    make_manager_user,
    make_supervisor_user,
    make_viewer_user,
)

STORES_PATH  = "/api/stores"
VENDORS_PATH = "/api/vendors"

SUPERVISOR_SCOPE_PARAMS   = {"scope_id": SUPERVISOR_SCOPE_ID}
SUPERVISOR_SCOPE_REQUIRED = "Supervisor scope required."


def test_manager_can_list_vendors(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    _create_vendor(client, name="Sysco")

    _authenticate_as(make_manager_user())

    response = client.get(VENDORS_PATH)

    assert response.status_code == 200

    names = {vendor["name"] for vendor in response.json()}

    assert "Sysco" in names


def test_viewer_can_list_vendors(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    _create_vendor(client, name="Sysco")

    _authenticate_as(make_viewer_user())

    response = client.get(VENDORS_PATH)

    assert response.status_code == 200

    names = {vendor["name"] for vendor in response.json()}

    assert "Sysco" in names


def test_manager_can_get_vendor(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    vendor_id = _create_vendor(client, name="Sysco")

    _authenticate_as(make_manager_user())

    response = client.get(_vendor_detail_path(vendor_id))

    assert response.status_code == 200
    assert response.json()["id"] == vendor_id


def test_manager_cannot_create_vendor(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_manager_user())

    response = api_context.client.post(
        VENDORS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_update_vendor(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    vendor_id = _create_vendor(client, name="Sysco")

    _authenticate_as(make_manager_user())

    response = client.put(
        _vendor_detail_path(vendor_id),
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Updated Sysco",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_delete_vendor(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    vendor_id = _create_vendor(client, name="Sysco")

    _authenticate_as(make_manager_user())

    response = client.delete(
        _vendor_detail_path(vendor_id),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_viewer_cannot_create_vendor(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_viewer_user())

    response = api_context.client.post(
        VENDORS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_supervisor_can_create_vendor(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_supervisor_user())

    response = api_context.client.post(
        VENDORS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Sysco"


def test_manager_cannot_list_stores(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_manager_user())

    response = api_context.client.get(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_viewer_cannot_list_stores(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_viewer_user())

    response = api_context.client.get(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_create_store(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_manager_user())

    response = api_context.client.post(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Ithaca Bakery",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_update_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    store_id = _create_store(client, name="Ithaca Bakery")

    _authenticate_as(make_manager_user())

    response = client.put(
        _store_detail_path(store_id),
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Updated Ithaca Bakery",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_manager_cannot_delete_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    store_id = _create_store(client, name="Ithaca Bakery")

    _authenticate_as(make_manager_user())

    response = client.delete(
        _store_detail_path(store_id),
        params=SUPERVISOR_SCOPE_PARAMS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == SUPERVISOR_SCOPE_REQUIRED


def test_supervisor_can_create_store(
    api_context: ApiTestContext,
) -> None:
    _authenticate_as(make_supervisor_user())

    response = api_context.client.post(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": "Ithaca Bakery",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Ithaca Bakery"


def _authenticate_as(user) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


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


def _create_vendor(client: TestClient, *, name: str) -> str:
    response = client.post(
        VENDORS_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": name,
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _store_detail_path(store_id: str) -> str:
    return f"{STORES_PATH}/{store_id}"


def _vendor_detail_path(vendor_id: str) -> str:
    return f"{VENDORS_PATH}/{vendor_id}"