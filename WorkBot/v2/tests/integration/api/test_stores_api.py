from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

STORES_PATH = "/api/stores"

def test_create_store(client: TestClient) -> None:
    response = client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "general_manager": "Andrew",
            "inventory_clerk": "Taylor",
            "address": "123 Bakery Lane",
            "phone_number": "555-123-4567",
            "special_notes": "Main production store",
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["name"] == "Ithaca Bakery"
    assert data["general_manager"] == "Andrew"
    assert data["inventory_clerk"] == "Taylor"
    assert data["address"] == "123 Bakery Lane"
    assert data["phone_number"] == "555-123-4567"
    assert data["special_notes"] == "Main production store"
    assert data["is_active"] is True
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_store_rejects_duplicate_name(client: TestClient) -> None:
    payload = {
        "name": "Ithaca Bakery",
        "is_active": True,
    }

    first_response = client.post(STORES_PATH, json=payload)
    duplicate_response = client.post(STORES_PATH, json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Store already exists: Ithaca Bakery"


def test_create_store_rejects_empty_name(client: TestClient) -> None:
    response = client.post(
        STORES_PATH,
        json={
            "name": "   ",
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "store name cannot be empty."


def test_list_stores(client: TestClient) -> None:
    client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "is_active": True,
        },
    )
    client.post(
        STORES_PATH,
        json={
            "name": "Collegetown Bagels",
            "is_active": True,
        },
    )

    response = client.get(STORES_PATH)

    assert response.status_code == 200

    data = response.json()
    names = {store["name"] for store in data}

    assert "Ithaca Bakery" in names
    assert "Collegetown Bagels" in names


def test_list_stores_can_search_by_name(client: TestClient) -> None:
    client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "is_active": True,
        },
    )
    client.post(
        STORES_PATH,
        json={
            "name": "Collegetown Bagels",
            "is_active": True,
        },
    )

    response = client.get(STORES_PATH, params={"search": "ithaca"})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Ithaca Bakery"


def test_list_stores_can_exclude_inactive(client: TestClient) -> None:
    client.post(
        STORES_PATH,
        json={
            "name": "Active Store",
            "is_active": True,
        },
    )
    client.post(
        STORES_PATH,
        json={
            "name": "Inactive Store",
            "is_active": False,
        },
    )

    response = client.get(STORES_PATH, params={"include_inactive": False})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Active Store"


def test_get_store(client: TestClient) -> None:
    create_response = client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "general_manager": "Andrew",
            "is_active": True,
        },
    )

    store_id = create_response.json()["id"]

    response = client.get(_store_detail_path(store_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == store_id
    assert data["name"] == "Ithaca Bakery"
    assert data["general_manager"] == "Andrew"


def test_get_store_returns_404_for_missing_store(client: TestClient) -> None:
    response = client.get(_store_detail_path("sto_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found: sto_missing"


def test_update_store(client: TestClient) -> None:
    create_response = client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "general_manager": "Old Manager",
            "inventory_clerk": "Old Clerk",
            "address": "Old Address",
            "phone_number": "555-000-0000",
            "special_notes": "Old notes",
            "is_active": True,
        },
    )

    store_id = create_response.json()["id"]
    created_at = create_response.json()["created_at"]
    original_updated_at = create_response.json()["updated_at"]

    response = client.put(
        _store_detail_path(store_id),
        json={
            "name": "Ithaca Bakery Updated",
            "general_manager": "Andrew",
            "inventory_clerk": "Taylor",
            "address": "123 Bakery Lane",
            "phone_number": "555-123-4567",
            "special_notes": "Updated notes",
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == store_id
    assert data["name"] == "Ithaca Bakery Updated"
    assert data["general_manager"] == "Andrew"
    assert data["inventory_clerk"] == "Taylor"
    assert data["address"] == "123 Bakery Lane"
    assert data["phone_number"] == "555-123-4567"
    assert data["special_notes"] == "Updated notes"
    assert data["is_active"] is True
    assert _parse_api_datetime(data["created_at"]) == _parse_api_datetime(created_at)
    assert _parse_api_datetime(data["updated_at"]) >= _parse_api_datetime(original_updated_at)


def test_update_store_returns_404_for_missing_store(client: TestClient) -> None:
    response = client.put(
        _store_detail_path("sto_missing"),
        json={
            "name": "Missing Store",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found: sto_missing"


def test_update_store_rejects_duplicate_name(client: TestClient) -> None:
    first_response = client.post(
        STORES_PATH,
        json={
            "name": "Original Store",
            "is_active": True,
        },
    )
    client.post(
        STORES_PATH,
        json={
            "name": "Duplicate Store",
            "is_active": True,
        },
    )

    store_id = first_response.json()["id"]

    response = client.put(
        _store_detail_path(store_id),
        json={
            "name": "Duplicate Store",
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Store already exists: Duplicate Store"


def test_delete_store_deactivates_store(client: TestClient) -> None:
    create_response = client.post(
        STORES_PATH,
        json={
            "name": "Ithaca Bakery",
            "is_active": True,
        },
    )

    store_id = create_response.json()["id"]
    created_at = create_response.json()["created_at"]
    original_updated_at = create_response.json()["updated_at"]

    delete_response = client.delete(_store_detail_path(store_id))

    assert delete_response.status_code == 200

    deleted = delete_response.json()

    assert deleted["id"] == store_id
    assert deleted["name"] == "Ithaca Bakery"
    assert deleted["is_active"] is False
    assert _parse_api_datetime(deleted["created_at"]) == _parse_api_datetime(created_at)
    assert _parse_api_datetime(deleted["updated_at"]) >= _parse_api_datetime(original_updated_at)

    get_response = client.get(_store_detail_path(store_id))

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_delete_store_returns_404_for_missing_store(client: TestClient) -> None:
    response = client.delete(_store_detail_path("sto_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found: sto_missing"


def _store_detail_path(store_id: str) -> str:
    return f"{STORES_PATH}/{store_id}"


def _parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)