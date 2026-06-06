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


ORDERS_PATH = "/api/orders"
STORES_PATH = "/api/stores"
VENDORS_PATH = "/api/vendors"


@dataclass(frozen=True)
class ApiTestContext:
    client: TestClient
    session_factory: sessionmaker[Session]


@pytest.fixture
def api_context(tmp_path: Path) -> Generator[ApiTestContext, None, None]:
    database_path = tmp_path / "test_order_permissions_api.db"
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


def test_manager_can_create_order_for_assigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": assigned_store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "quantity": "2",
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["store_id"] == assigned_store_id
    assert data["store_name"] == "Ithaca Bakery"


def test_manager_cannot_create_order_for_unassigned_store(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    unassigned_store_id = _create_store(client, name="Collegetown Bagels")
    vendor_id = _create_vendor(client, name="Sysco")

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": unassigned_store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "quantity": "2",
                }
            ],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot create order for this store."


def test_manager_can_view_assigned_store_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.get(_order_detail_path(order_id))

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_manager_cannot_view_unassigned_store_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    assigned_store_id = _create_store(client, name="Ithaca Bakery")
    unassigned_store_id = _create_store(client, name="Collegetown Bagels")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=unassigned_store_id,
        vendor_id=vendor_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=assigned_store_id,
    )
    _authenticate_as(manager)

    response = client.get(_order_detail_path(order_id))

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access order for another store."


def test_manager_can_cancel_assigned_store_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.post(
        _order_cancel_path(order_id),
        json={
            "reason": "Duplicate",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_viewer_can_view_assigned_store_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    viewer = make_viewer_user()
    _grant_store_access(
        api_context,
        user_id=viewer.id,
        store_id=store_id,
    )
    _authenticate_as(viewer)

    response = client.get(_order_detail_path(order_id))

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_viewer_cannot_create_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")

    viewer = make_viewer_user()
    _grant_store_access(
        api_context,
        user_id=viewer.id,
        store_id=store_id,
    )
    _authenticate_as(viewer)

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "quantity": "2",
                }
            ],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Viewer users cannot create orders."


def test_viewer_cannot_cancel_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    viewer = make_viewer_user()
    _grant_store_access(
        api_context,
        user_id=viewer.id,
        store_id=store_id,
    )
    _authenticate_as(viewer)

    response = client.post(
        _order_cancel_path(order_id),
        json={
            "reason": "Viewer should not cancel",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Viewer users cannot modify orders."


def test_manager_cannot_export_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.post(_order_export_path(order_id))

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_manager_cannot_delete_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    manager = make_manager_user()
    _grant_store_access(
        api_context,
        user_id=manager.id,
        store_id=store_id,
    )
    _authenticate_as(manager)

    response = client.delete(_order_detail_path(order_id))

    assert response.status_code == 403
    assert response.json()["detail"] == "Supervisor access required."


def test_supervisor_can_export_order(
    api_context: ApiTestContext,
) -> None:
    client = api_context.client

    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    _authenticate_as(make_supervisor_user())

    response = client.post(_order_export_path(order_id))

    assert response.status_code == 200
    assert response.json()["status"] == "exported"


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


def _create_vendor(client: TestClient, *, name: str) -> str:
    response = client.post(
        VENDORS_PATH,
        json={
            "name": name,
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _create_order(
    client: TestClient,
    *,
    store_id: str,
    vendor_id: str,
) -> str:
    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "source_vendor_sku": "SYS-MALT",
                    "quantity": "2",
                    "unit": "case",
                }
            ],
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _order_detail_path(order_id: str) -> str:
    return f"{ORDERS_PATH}/{order_id}"


def _order_cancel_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/cancel"


def _order_export_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/export"