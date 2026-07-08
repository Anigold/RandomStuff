from __future__ import annotations

from dataclasses import replace
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

STORE_SCOPES_PATH = "/api/store-scopes"
STORES_PATH = "/api/stores"

SUPERVISOR_SCOPE_PARAMS = {"scope_id": SUPERVISOR_SCOPE_ID}


def test_supervisor_sees_supervisor_scope_and_assigned_stores(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    supervisor = make_supervisor_user()
    _authenticate_as(supervisor)

    ithaca_store_id = _create_store(client, name="Ithaca Bakery")
    collegetown_store_id = _create_store(client, name="Collegetown Bagels")
    _create_store(client, name="Unassigned Store")

    _grant_store_access(
        api_context,
        user_id=supervisor.id,
        store_id=ithaca_store_id,
    )
    _grant_store_access(
        api_context,
        user_id=supervisor.id,
        store_id=collegetown_store_id,
    )

    response = client.get(STORE_SCOPES_PATH)

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "id": SUPERVISOR_SCOPE_ID,
            "name": "Supervisor",
            "type": "supervisor",
        },
        {
            "id": ithaca_store_id,
            "name": "Ithaca Bakery",
            "type": "store",
        },
        {
            "id": collegetown_store_id,
            "name": "Collegetown Bagels",
            "type": "store",
        },
    ]


def test_manager_sees_assigned_stores_only(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    _create_store(client, name="Unassigned Store")

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(STORE_SCOPES_PATH)

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "id": assigned_store_id,
            "name": "Ithaca Bakery",
            "type": "store",
        },
    ]


def test_viewer_sees_assigned_stores_only(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    _create_store(client, name="Unassigned Store")

    viewer = make_viewer_user()
    _grant_store_access(
        api_context,
        user_id=viewer.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(viewer)

    response = client.get(STORE_SCOPES_PATH)

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "id": assigned_store_id,
            "name": "Ithaca Bakery",
            "type": "store",
        },
    ]


def test_unassigned_user_sees_empty_store_scope_list(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())
    _create_store(client, name="Ithaca Bakery")

    manager = make_manager_user()
    _authenticate_as(manager)

    response = client.get(STORE_SCOPES_PATH)

    assert response.status_code == 200
    assert response.json() == []


def test_inactive_assigned_store_is_excluded_from_store_scopes(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    _authenticate_as(make_supervisor_user())

    active_store_id = _create_store(
        client,
        name="Active Store",
        is_active=True,
    )
    inactive_store_id = _create_store(
        client,
        name="Inactive Store",
        is_active=False,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=active_store_id,
    )
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=inactive_store_id,
    )
    _authenticate_as(manager)

    response = client.get(STORE_SCOPES_PATH)

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            "id": active_store_id,
            "name": "Active Store",
            "type": "store",
        },
    ]


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


def _create_store(
    client: TestClient,
    *,
    name: str,
    is_active: bool = True,
) -> str:
    response = client.post(
        STORES_PATH,
        params=SUPERVISOR_SCOPE_PARAMS,
        json={
            "name": name,
            "is_active": is_active,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]