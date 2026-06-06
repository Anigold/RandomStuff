from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.auth.dependencies import get_current_user
from apps.api.dependencies import get_db_session
from apps.api.main import app
from tests.helpers.auth_helpers import (
    make_manager_user,
    make_supervisor_user,
    make_user_store_access,
    make_viewer_user,
)
from workbot_core.infrastructure.database.base import Base
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserStoreAccessRepository,
)


ITEMS_PATH = "/api/items"
STORES_PATH = "/api/stores"


@dataclass(frozen=True)
class ApiTestContext:
    client: TestClient
    session_factory: sessionmaker[Session]


@pytest.fixture
def api_context(tmp_path: Path) -> Generator[ApiTestContext, None, None]:
    database_path = tmp_path / "test_item_permissions_api.db"
    database_url = f"sqlite:///{database_path}"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db_session() -> Generator[Session, None, None]:
        session = session_factory()

        try:
            yield session
        finally:
            session.close()

    supervisor = make_supervisor_user()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = lambda: supervisor

    with TestClient(app) as test_client:
        yield ApiTestContext(
            client=test_client,
            session_factory=session_factory,
        )

    app.dependency_overrides.clear()
    engine.dispose()


def test_manager_can_list_items_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

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
            "store": "Ithaca Bakery",
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

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    _create_store(client, name="Collegetown Bagels")

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
            "store": "Collegetown Bagels",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access this store."


def test_manager_can_get_assigned_store_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

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

    response = client.get(_item_detail_path(item_id))

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

    response = client.get(_item_detail_path(item_id))

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access item for assigned stores."


def test_manager_cannot_create_item(
    api_context: ApiTestContext,
) -> None:
    manager = make_manager_user()
    _authenticate_as(manager)

    response = api_context.client.post(
        ITEMS_PATH,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_manager_cannot_update_item(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    item_id = _create_item(client, name="Malt Barrel")

    manager = make_manager_user()
    _authenticate_as(manager)

    response = client.put(
        _item_detail_path(item_id),
        json={
            "name": "Updated Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_manager_cannot_delete_item(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    item_id = _create_item(client, name="Malt Barrel")

    manager = make_manager_user()
    _authenticate_as(manager)

    response = client.delete(_item_detail_path(item_id))

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_viewer_can_get_assigned_store_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

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

    response = client.get(_item_detail_path(item_id))

    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_viewer_cannot_create_item(
    api_context: ApiTestContext,
) -> None:
    viewer = make_viewer_user()
    _authenticate_as(viewer)

    response = api_context.client.post(
        ITEMS_PATH,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_supervisor_can_get_full_item_detail(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    item_id = _create_item(client, name="Malt Barrel")

    _add_item_store_info(
        client,
        item_id=item_id,
        store_id=store_id,
    )

    _authenticate_as(make_supervisor_user())

    response = client.get(_item_detail_path(item_id))

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