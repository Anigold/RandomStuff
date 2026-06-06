from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.dependencies import get_db_session
from apps.api.main import app
from workbot_core.infrastructure.database.base import Base

from apps.api.auth.dependencies import get_current_user
from tests.helpers.auth_helpers import make_supervisor_user

VENDORS_PATH = "/api/vendors"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
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
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_create_vendor(client: TestClient) -> None:
    response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "order_format": "email",
            "special_notes": "Primary broadline vendor",
            "min_order_value": "250.00",
            "min_order_cases": 5,
            "internal_contacts": [
                {
                    "name": "Jamie",
                    "title": "Sales Rep",
                    "email": "jamie@sysco.example",
                    "phone": "555-123-4567",
                }
            ],
            "ordering": {
                "method": ["email", "portal"],
                "email": "orders@sysco.example",
                "portal_url": "https://vendor.example/orders",
                "phone_number": "555-765-4321",
                "schedule": [
                    {
                        "order_day": "Monday",
                        "delivery_days": ["Wednesday", "Friday"],
                        "cutoff_time": "14:00",
                    }
                ],
            },
            "store_references": [
                {
                    "store_id": "sto_ithaca",
                    "vendor_store_reference": "ITH001"
                },
                {
                    "store_id": "sto_collegetown",
                    "vendor_store_reference": ""
                }
            ],
            "is_active": True,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["name"] == "Sysco"
    assert data["order_format"] == "email"
    assert data["special_notes"] == "Primary broadline vendor"
    assert data["min_order_value"] == "250.00"
    assert data["min_order_cases"] == 5
    assert data["internal_contacts"] == [
        {
            "name": "Jamie",
            "title": "Sales Rep",
            "email": "jamie@sysco.example",
            "phone": "555-123-4567",
        }
    ]
    assert data["ordering"] == {
        "method": ["email", "portal"],
        "email": "orders@sysco.example",
        "portal_url": "https://vendor.example/orders",
        "phone_number": "555-765-4321",
        "schedule": [
            {
                "order_day": "Monday",
                "delivery_days": ["Wednesday", "Friday"],
                "cutoff_time": "14:00",
            }
        ],
    }
    assert data["store_references"] == [
        {
            "store_id": "sto_ithaca",
            "vendor_store_reference": "ITH001",
        },
        {
            "store_id": "sto_collegetown",
            "vendor_store_reference": "",
        },
    ]
    assert data["is_active"] is True
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_vendor_rejects_duplicate_name(client: TestClient) -> None:
    payload = {
        "name": "Sysco",
        "is_active": True,
    }

    first_response = client.post(VENDORS_PATH, json=payload)
    duplicate_response = client.post(VENDORS_PATH, json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Vendor already exists: Sysco"


def test_create_vendor_rejects_empty_name(client: TestClient) -> None:
    response = client.post(
        VENDORS_PATH,
        json={
            "name": "   ",
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "vendor name cannot be empty."


def test_create_vendor_rejects_empty_contact_name(client: TestClient) -> None:
    response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "internal_contacts": [
                {
                    "name": "   ",
                    "title": "Sales Rep",
                }
            ],
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "contact name cannot be empty."


def test_create_vendor_rejects_empty_schedule_order_day(client: TestClient) -> None:
    response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "ordering": {
                "schedule": [
                    {
                        "order_day": "   ",
                    }
                ],
            },
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "order day cannot be empty."


def test_list_vendors(client: TestClient) -> None:
    client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )
    client.post(
        VENDORS_PATH,
        json={
            "name": "Regional Produce",
            "is_active": True,
        },
    )

    response = client.get(VENDORS_PATH)

    assert response.status_code == 200

    data = response.json()
    names = {vendor["name"] for vendor in data}

    assert "Sysco" in names
    assert "Regional Produce" in names


def test_list_vendors_can_search_by_name(client: TestClient) -> None:
    client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )
    client.post(
        VENDORS_PATH,
        json={
            "name": "Regional Produce",
            "is_active": True,
        },
    )

    response = client.get(VENDORS_PATH, params={"search": "sys"})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Sysco"


def test_list_vendors_can_exclude_inactive(client: TestClient) -> None:
    client.post(
        VENDORS_PATH,
        json={
            "name": "Active Vendor",
            "is_active": True,
        },
    )
    client.post(
        VENDORS_PATH,
        json={
            "name": "Inactive Vendor",
            "is_active": False,
        },
    )

    response = client.get(VENDORS_PATH, params={"include_inactive": False})

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Active Vendor"


def test_get_vendor(client: TestClient) -> None:
    create_response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "order_format": "email",
            "is_active": True,
        },
    )

    vendor_id = create_response.json()["id"]

    response = client.get(_vendor_detail_path(vendor_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vendor_id
    assert data["name"] == "Sysco"
    assert data["order_format"] == "email"


def test_get_vendor_returns_404_for_missing_vendor(client: TestClient) -> None:
    response = client.get(_vendor_detail_path("ven_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found: ven_missing"


def test_update_vendor(client: TestClient) -> None:
    create_response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "order_format": "old",
            "special_notes": "Old notes",
            "min_order_value": "100.00",
            "min_order_cases": 1,
            "is_active": True,
        },
    )

    vendor_id = create_response.json()["id"]
    created_at = create_response.json()["created_at"]
    original_updated_at = create_response.json()["updated_at"]

    response = client.put(
        _vendor_detail_path(vendor_id),
        json={
            "name": "Sysco Updated",
            "order_format": "email",
            "special_notes": "Updated notes",
            "min_order_value": "250.00",
            "min_order_cases": 5,
            "internal_contacts": [
                {
                    "name": "Jamie",
                    "title": "Sales Rep",
                    "email": "jamie@sysco.example",
                    "phone": "555-123-4567",
                }
            ],
            "ordering": {
                "method": ["email"],
                "email": "orders@sysco.example",
                "schedule": [
                    {
                        "order_day": "Monday",
                        "delivery_days": ["Wednesday"],
                        "cutoff_time": "14:00",
                    }
                ],
            },
            "store_references": [
                {
                    "store_id": "sto_ithaca",
                    "vendor_store_reference": "ITH001",
                },
            ],
            "is_active": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vendor_id
    assert data["name"] == "Sysco Updated"
    assert data["order_format"] == "email"
    assert data["special_notes"] == "Updated notes"
    assert data["min_order_value"] == "250.00"
    assert data["min_order_cases"] == 5
    assert data["internal_contacts"] == [
        {
            "name": "Jamie",
            "title": "Sales Rep",
            "email": "jamie@sysco.example",
            "phone": "555-123-4567",
        }
    ]
    assert data["ordering"]["method"] == ["email"]
    assert data["ordering"]["email"] == "orders@sysco.example"
    assert data["ordering"]["schedule"] == [
        {
            "order_day": "Monday",
            "delivery_days": ["Wednesday"],
            "cutoff_time": "14:00",
        }
    ]
    assert data["store_references"] == [
        {
            "store_id": "sto_ithaca",
            "vendor_store_reference": "ITH001",
        },
    ]
    assert data["is_active"] is True
    assert _parse_api_datetime(data["created_at"]) == _parse_api_datetime(created_at)
    assert _parse_api_datetime(data["updated_at"]) >= _parse_api_datetime(original_updated_at)


def test_update_vendor_returns_404_for_missing_vendor(client: TestClient) -> None:
    response = client.put(
        _vendor_detail_path("ven_missing"),
        json={
            "name": "Missing Vendor",
            "is_active": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found: ven_missing"


def test_update_vendor_rejects_duplicate_name(client: TestClient) -> None:
    first_response = client.post(
        VENDORS_PATH,
        json={
            "name": "Original Vendor",
            "is_active": True,
        },
    )
    client.post(
        VENDORS_PATH,
        json={
            "name": "Duplicate Vendor",
            "is_active": True,
        },
    )

    vendor_id = first_response.json()["id"]

    response = client.put(
        _vendor_detail_path(vendor_id),
        json={
            "name": "Duplicate Vendor",
            "is_active": True,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Vendor already exists: Duplicate Vendor"


def test_delete_vendor_deactivates_vendor(client: TestClient) -> None:
    create_response = client.post(
        VENDORS_PATH,
        json={
            "name": "Sysco",
            "is_active": True,
        },
    )

    vendor_id = create_response.json()["id"]
    created_at = create_response.json()["created_at"]
    original_updated_at = create_response.json()["updated_at"]

    delete_response = client.delete(_vendor_detail_path(vendor_id))

    assert delete_response.status_code == 200

    deleted = delete_response.json()

    assert deleted["id"] == vendor_id
    assert deleted["name"] == "Sysco"
    assert deleted["is_active"] is False
    assert _parse_api_datetime(deleted["created_at"]) == _parse_api_datetime(created_at)
    assert _parse_api_datetime(deleted["updated_at"]) >= _parse_api_datetime(original_updated_at)

    get_response = client.get(_vendor_detail_path(vendor_id))

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_delete_vendor_returns_404_for_missing_vendor(client: TestClient) -> None:
    response = client.delete(_vendor_detail_path("ven_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found: ven_missing"


def _vendor_detail_path(vendor_id: str) -> str:
    return f"{VENDORS_PATH}/{vendor_id}"


def _parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)