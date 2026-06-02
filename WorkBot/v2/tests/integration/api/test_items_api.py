from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.dependencies import get_db_session
from apps.api.main import app
from workbot_core.infrastructure.database.base import Base


ITEMS_PATH = "/api/items"
VENDORS_PATH = "/api/vendors"
STORES_PATH = "/api/stores"

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
    response = client.post(
        ITEMS_PATH,
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
    payload = {
        "name": "Malt Barrel",
        "category": "Dry Goods",
        "is_active": True,
    }

    first_response = client.post(ITEMS_PATH, json=payload)
    duplicate_response = client.post(ITEMS_PATH, json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Item already exists: Malt Barrel"


def test_list_items(client: TestClient) -> None:
    client.post(
        ITEMS_PATH,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        ITEMS_PATH,
        json={
            "name": "Flour Bag",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    response = client.get(ITEMS_PATH)

    assert response.status_code == 200

    data = response.json()
    names = {item["name"] for item in data}

    assert "Malt Barrel" in names
    assert "Flour Bag" in names


def test_list_items_can_search_by_name(client: TestClient) -> None:
    client.post(
        ITEMS_PATH,
        json={
            "name": "Malt Barrel",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        ITEMS_PATH,
        json={
            "name": "Flour Bag",
            "category": "Dry Goods",
            "is_active": True,
        },
    )

    response = client.get(ITEMS_PATH, params={"search": "malt"})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Malt Barrel"


def test_get_item_detail(client: TestClient) -> None:
    create_response = client.post(
        ITEMS_PATH,
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
    create_response = client.post(
        ITEMS_PATH,
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
    first_response = client.post(
        ITEMS_PATH,
        json={
            "name": "Original Item",
            "category": "Dry Goods",
            "is_active": True,
        },
    )
    client.post(
        ITEMS_PATH,
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
    create_response = client.post(
        ITEMS_PATH,
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


def test_add_item_vendor_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    vendor_id = _create_vendor(client, name="Sysco")

    response = client.post(
        _item_vendor_info_collection_path(item_id),
        json={
            "vendor_id": vendor_id,
            "vendor_sku": "SYS-MALT",
            "purchase_unit": "case",
            "pack_size": "12",
            "price": "42.50",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["item_id"] == item_id
    assert data["vendor_id"] == vendor_id
    assert data["vendor_sku"] == "SYS-MALT"
    assert data["purchase_unit"] == "case"
    assert Decimal(data["pack_size"]) == Decimal("12")
    assert Decimal(data["price"]) == Decimal("42.50")
    assert data["is_active"] is True


def test_update_item_vendor_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    vendor_id = _create_vendor(client, name="Sysco")
    info_id = _add_item_vendor_info(client, item_id=item_id, vendor_id=vendor_id)

    response = client.put(
        _item_vendor_info_detail_path(item_id, info_id),
        json={
            "vendor_sku": "UPDATED-SKU",
            "purchase_unit": "bag",
            "pack_size": "24",
            "price": "84.75",
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == info_id
    assert data["item_id"] == item_id
    assert data["vendor_id"] == vendor_id
    assert data["vendor_sku"] == "UPDATED-SKU"
    assert data["purchase_unit"] == "bag"
    assert Decimal(data["pack_size"]) == Decimal("24")
    assert Decimal(data["price"]) == Decimal("84.75")
    assert data["is_active"] is True


def test_update_item_vendor_info_returns_404_for_missing_info(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")

    response = client.put(
        _item_vendor_info_detail_path(item_id, "ivi_missing"),
        json={
            "vendor_sku": "UPDATED-SKU",
            "purchase_unit": "bag",
            "pack_size": "24",
            "price": "84.75",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item vendor info not found: ivi_missing"


def test_update_item_vendor_info_returns_404_for_wrong_item(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    other_item_id = _create_item(client, name="Flour Bag")
    vendor_id = _create_vendor(client, name="Sysco")
    info_id = _add_item_vendor_info(client, item_id=item_id, vendor_id=vendor_id)

    response = client.put(
        _item_vendor_info_detail_path(other_item_id, info_id),
        json={
            "vendor_sku": "UPDATED-SKU",
            "purchase_unit": "bag",
            "pack_size": "24",
            "price": "84.75",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Item vendor info not found: {info_id}"


def test_delete_item_vendor_info_deactivates_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    vendor_id = _create_vendor(client, name="Sysco")
    info_id = _add_item_vendor_info(client, item_id=item_id, vendor_id=vendor_id)

    response = client.delete(
        _item_vendor_info_detail_path(item_id, info_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == info_id
    assert data["item_id"] == item_id
    assert data["vendor_id"] == vendor_id
    assert data["is_active"] is False


def test_delete_item_vendor_info_returns_404_for_missing_info(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")

    response = client.delete(
        _item_vendor_info_detail_path(item_id, "ivi_missing"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item vendor info not found: ivi_missing"


def test_delete_item_vendor_info_returns_404_for_wrong_item(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    other_item_id = _create_item(client, name="Flour Bag")
    vendor_id = _create_vendor(client, name="Sysco")
    info_id = _add_item_vendor_info(client, item_id=item_id, vendor_id=vendor_id)

    response = client.delete(
        _item_vendor_info_detail_path(other_item_id, info_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Item vendor info not found: {info_id}"

def test_add_item_store_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    store_id = _create_store(client, name="Ithaca Bakery")

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

    data = response.json()

    assert data["id"]
    assert data["item_id"] == item_id
    assert data["store_id"] == store_id
    assert data["count_unit"] == "bag"
    assert Decimal(data["par"]) == Decimal("6")
    assert data["is_active"] is True


def test_update_item_store_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    store_id = _create_store(client, name="Ithaca Bakery")
    info_id = _add_item_store_info(client, item_id=item_id, store_id=store_id)

    response = client.put(
        _item_store_info_detail_path(item_id, info_id),
        json={
            "count_unit": "case",
            "par": "12",
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == info_id
    assert data["item_id"] == item_id
    assert data["store_id"] == store_id
    assert data["count_unit"] == "case"
    assert Decimal(data["par"]) == Decimal("12")
    assert data["is_active"] is True


def test_update_item_store_info_returns_404_for_missing_info(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")

    response = client.put(
        _item_store_info_detail_path(item_id, "isi_missing"),
        json={
            "count_unit": "case",
            "par": "12",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item store info not found: isi_missing"


def test_update_item_store_info_returns_404_for_wrong_item(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    other_item_id = _create_item(client, name="Flour Bag")
    store_id = _create_store(client, name="Ithaca Bakery")
    info_id = _add_item_store_info(client, item_id=item_id, store_id=store_id)

    response = client.put(
        _item_store_info_detail_path(other_item_id, info_id),
        json={
            "count_unit": "case",
            "par": "12",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Item store info not found: {info_id}"


def test_delete_item_store_info_deactivates_info(client: TestClient) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    store_id = _create_store(client, name="Ithaca Bakery")
    info_id = _add_item_store_info(client, item_id=item_id, store_id=store_id)

    response = client.delete(
        _item_store_info_detail_path(item_id, info_id),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == info_id
    assert data["item_id"] == item_id
    assert data["store_id"] == store_id
    assert data["is_active"] is False


def test_delete_item_store_info_returns_404_for_missing_info(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")

    response = client.delete(
        _item_store_info_detail_path(item_id, "isi_missing"),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item store info not found: isi_missing"


def test_delete_item_store_info_returns_404_for_wrong_item(
    client: TestClient,
) -> None:
    item_id = _create_item(client, name="Malt Barrel")
    other_item_id = _create_item(client, name="Flour Bag")
    store_id = _create_store(client, name="Ithaca Bakery")
    info_id = _add_item_store_info(client, item_id=item_id, store_id=store_id)

    response = client.delete(
        _item_store_info_detail_path(other_item_id, info_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == f"Item store info not found: {info_id}"


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


def _add_item_vendor_info(
    client: TestClient,
    *,
    item_id: str,
    vendor_id: str,
) -> str:
    response = client.post(
        _item_vendor_info_collection_path(item_id),
        json={
            "vendor_id": vendor_id,
            "vendor_sku": "SYS-MALT",
            "purchase_unit": "case",
            "pack_size": "12",
            "price": "42.50",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def _item_detail_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}"


def _item_vendor_info_collection_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}/vendor-info"


def _item_vendor_info_detail_path(item_id: str, info_id: str) -> str:
    return f"{_item_vendor_info_collection_path(item_id)}/{info_id}"

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


def _item_store_info_collection_path(item_id: str) -> str:
    return f"{ITEMS_PATH}/{item_id}/store-info"


def _item_store_info_detail_path(item_id: str, info_id: str) -> str:
    return f"{_item_store_info_collection_path(item_id)}/{info_id}"