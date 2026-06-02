from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.dependencies import get_db_session
from apps.api.main import app
from workbot_core.infrastructure.database.base import Base


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    database_path = tmp_path / "test_items_api.db"
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

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    engine.dispose()


def test_create_item(client: TestClient) -> None:
    items_path = _items_collection_path()

    response = client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "subcategory": "B&B Ingredients",
            "count_unit_quantity": "360.000",
            "count_unit_measure": "lb",
            "weight_quantity": "360.000",
            "weight_measure": "lb",
            "volume_quantity": "30.000",
            "volume_measure": "gal",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"].startswith("itm_")
    assert data["name"] == "Malt Barrel"
    assert data["category"] == "Dry Goods"
    assert data["subcategory"] == "B&B Ingredients"
    assert data["count_unit_quantity"] == "360.000"
    assert data["count_unit_measure"] == "lb"
    assert data["weight_quantity"] == "360.000"
    assert data["weight_measure"] == "lb"
    assert data["volume_quantity"] == "30.000"
    assert data["volume_measure"] == "gal"
    assert data["is_active"] is True


def test_create_item_rejects_duplicate_name(client: TestClient) -> None:
    items_path = _items_collection_path()

    payload = {
        "name": "Malt Barrel",
        "category": "Dry Goods",
        "is_active": True,
    }

    first_response = client.post(items_path, json=payload)
    duplicate_response = client.post(items_path, json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Item already exists: Malt Barrel"


def test_list_items(client: TestClient) -> None:
    items_path = _items_collection_path()

    client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        items_path,
        json={
            "name": "Flour Bag",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    response = client.get(items_path)

    assert response.status_code == 200

    data = response.json()
    names = {item["name"] for item in data}

    assert "Malt Barrel" in names
    assert "Flour Bag" in names


def test_list_items_can_search_by_name(client: TestClient) -> None:
    items_path = _items_collection_path()

    client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        items_path,
        json={
            "name": "Flour Bag",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    response = client.get(items_path, params={"search": "malt"})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Malt Barrel"


def test_get_item_detail(client: TestClient) -> None:
    items_path = _items_collection_path()

    create_response = client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "subcategory": "B&B Ingredients",
            "is_active": True,
        },
    )

    item_id = create_response.json()["id"]

    response = client.get(_item_detail_path(item_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "Malt Barrel"
    assert data["category"] == "Dry Goods"
    assert data["subcategory"] == "B&B Ingredients"
    assert data["vendor_info"] == []
    assert data["store_info"] == []


def test_get_item_detail_returns_404_for_missing_item(client: TestClient) -> None:
    response = client.get(_item_detail_path("itm_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found: itm_missing"


def test_update_item(client: TestClient) -> None:
    items_path = _items_collection_path()

    create_response = client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "subcategory": "Old Subcategory",
            "is_active": True,
        },
    )

    item_id = create_response.json()["id"]

    response = client.put(
        _item_detail_path(item_id),
        json={
            "name": "Malt Barrel Updated",
            "category": "Dry Goods",
            "subcategory": "B&B Ingredients",
            "count_unit_quantity": "360.000",
            "count_unit_measure": "lb",
            "weight_quantity": "360.000",
            "weight_measure": "lb",
            "volume_quantity": "30.000",
            "volume_measure": "gal",
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == item_id
    assert data["name"] == "Malt Barrel Updated"
    assert data["category"] == "Dry Goods"
    assert data["subcategory"] == "B&B Ingredients"
    assert data["count_unit_quantity"] == "360.000"
    assert data["count_unit_measure"] == "lb"
    assert data["weight_quantity"] == "360.000"
    assert data["weight_measure"] == "lb"
    assert data["volume_quantity"] == "30.000"
    assert data["volume_measure"] == "gal"
    assert data["is_active"] is True


def test_update_item_returns_404_for_missing_item(client: TestClient) -> None:
    response = client.put(
        _item_detail_path("itm_missing"),
        json={
            "name": "Missing Item",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found: itm_missing"


def test_update_item_rejects_duplicate_name(client: TestClient) -> None:
    items_path = _items_collection_path()

    first_response = client.post(
        items_path,
        json={
            "name": "Original Item",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        items_path,
        json={
            "name": "Duplicate Item",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    item_id = first_response.json()["id"]

    response = client.put(
        _item_detail_path(item_id),
        json={
            "name": "Duplicate Item",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Item already exists: Duplicate Item"


def test_delete_item_deactivates_item(client: TestClient) -> None:
    items_path = _items_collection_path()

    create_response = client.post(
        items_path,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    item_id = create_response.json()["id"]

    delete_response = client.delete(_item_detail_path(item_id))

    assert delete_response.status_code == 200

    deleted = delete_response.json()

    assert deleted["id"] == item_id
    assert deleted["name"] == "Malt Barrel"
    assert deleted["is_active"] is False

    get_response = client.get(_item_detail_path(item_id))

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_delete_item_returns_404_for_missing_item(client: TestClient) -> None:
    response = client.delete(_item_detail_path("itm_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found: itm_missing"


def _items_collection_path() -> str:
    for route in app.routes:
        if getattr(route, "name", None) == "create_item":
            return route.path

    raise AssertionError(
        "Could not find FastAPI route named 'create_item'. "
        "Check that apps.api.main includes the items router."
    )


def _item_detail_path(item_id: str) -> str:
    for route in app.routes:
        if getattr(route, "name", None) == "get_item":
            return route.path.replace("{item_id}", item_id)

    raise AssertionError(
        "Could not find FastAPI route named 'get_item'. "
        "Check that apps.api.main includes the items router."
    )