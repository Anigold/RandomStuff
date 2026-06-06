from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.dependencies import get_db_session
from apps.api.main import app
from workbot_core.infrastructure.database.base import Base

from apps.api.auth.dependencies import get_current_user
from tests.helpers.auth_helpers import make_supervisor_user


ORDERS_PATH = "/api/orders"
STORES_PATH = "/api/stores"
VENDORS_PATH = "/api/vendors"


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    database_path = tmp_path / "test_orders_api.db"
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
        yield test_client

    app.dependency_overrides.clear()
    engine.dispose()


def test_create_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "delivery_date": "2026-06-04",
            "notes": "Manual test order",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "source_vendor_sku": "SYS-MALT",
                    "quantity": "2",
                    "unit": "case",
                    "notes": "Need for weekend prep",
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"].startswith("ord_")
    assert data["store_id"] == store_id
    assert data["store_name"] == "Ithaca Bakery"
    assert data["vendor_id"] == vendor_id
    assert data["vendor_name"] == "Sysco"
    assert data["order_date"] == "2026-06-02"
    assert data["delivery_date"] == "2026-06-04"
    assert data["status"] == "pending"
    assert data["notes"] == "Manual test order"
    assert data["line_count"] == 1
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    assert len(data["lines"]) == 1

    line = data["lines"][0]

    assert line["id"].startswith("orl_")
    assert line["order_id"] == data["id"]
    assert line["status"] == "pending"
    assert line["source_item_name"] == "Malt Barrel"
    assert line["source_vendor_sku"] == "SYS-MALT"
    assert Decimal(line["quantity"]) == Decimal("2")
    assert line["unit"] == "case"
    assert line["notes"] == "Need for weekend prep"
    assert line["created_at"] is not None
    assert line["updated_at"] is not None


def test_create_order_rejects_missing_store(client: TestClient) -> None:
    vendor_id = _create_vendor(client, name="Sysco")

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": "str_missing",
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

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found: str_missing"


def test_create_order_rejects_missing_vendor(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": store_id,
            "vendor_id": "ven_missing",
            "order_date": "2026-06-02",
            "lines": [
                {
                    "source_item_name": "Malt Barrel",
                    "quantity": "2",
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found: ven_missing"


def test_create_order_rejects_empty_lines(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")

    response = client.post(
        ORDERS_PATH,
        json={
            "store_id": store_id,
            "vendor_id": vendor_id,
            "order_date": "2026-06-02",
            "lines": [],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Order must contain at least one line."


def test_list_orders(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")

    first_order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
        order_date="2026-06-02",
    )
    second_order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
        order_date="2026-06-03",
    )

    response = client.get(ORDERS_PATH)

    assert response.status_code == 200

    data = response.json()
    ids = {order["id"] for order in data}

    assert first_order_id in ids
    assert second_order_id in ids


def test_list_orders_can_filter_by_store_vendor_and_date_range(
    client: TestClient,
) -> None:
    ithaca_store_id = _create_store(client, name="Ithaca Bakery")
    collegetown_store_id = _create_store(client, name="Collegetown Bagels")

    sysco_vendor_id = _create_vendor(client, name="Sysco")
    regional_vendor_id = _create_vendor(client, name="Regional Produce")

    included_order_id = _create_order(
        client,
        store_id=ithaca_store_id,
        vendor_id=sysco_vendor_id,
        order_date="2026-06-02",
    )
    _create_order(
        client,
        store_id=ithaca_store_id,
        vendor_id=sysco_vendor_id,
        order_date="2026-05-01",
    )
    _create_order(
        client,
        store_id=collegetown_store_id,
        vendor_id=sysco_vendor_id,
        order_date="2026-06-02",
    )
    _create_order(
        client,
        store_id=ithaca_store_id,
        vendor_id=regional_vendor_id,
        order_date="2026-06-02",
    )

    response = client.get(
        ORDERS_PATH,
        params={
            "store": "Ithaca Bakery",
            "vendor": "Sysco",
            "start_date": "2026-06-01",
            "end_date": "2026-06-30",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == included_order_id
    assert data[0]["store_name"] == "Ithaca Bakery"
    assert data[0]["vendor_name"] == "Sysco"


def test_list_orders_returns_404_for_missing_store_filter(
    client: TestClient,
) -> None:
    response = client.get(
        ORDERS_PATH,
        params={
            "store": "Missing Store",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found: Missing Store"


def test_list_orders_returns_404_for_missing_vendor_filter(
    client: TestClient,
) -> None:
    response = client.get(
        ORDERS_PATH,
        params={
            "vendor": "Missing Vendor",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found: Missing Vendor"


def test_get_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
        order_date="2026-06-02",
    )

    response = client.get(_order_detail_path(order_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["store_id"] == store_id
    assert data["store_name"] == "Ithaca Bakery"
    assert data["vendor_id"] == vendor_id
    assert data["vendor_name"] == "Sysco"
    assert data["order_date"] == "2026-06-02"
    assert data["status"] == "pending"
    assert data["line_count"] == 1
    assert len(data["lines"]) == 1


def test_get_order_returns_404_for_missing_order(client: TestClient) -> None:
    response = client.get(_order_detail_path("ord_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found: ord_missing"


def test_update_order_notes(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
        notes="Old notes",
    )

    get_response = client.get(_order_detail_path(order_id))
    original_updated_at = get_response.json()["updated_at"]

    response = client.patch(
        _order_notes_path(order_id),
        json={
            "notes": "Updated notes",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["notes"] == "Updated notes"
    assert _parse_api_datetime(data["updated_at"]) >= _parse_api_datetime(
        original_updated_at
    )


def test_cancel_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
        notes="Original note",
    )

    response = client.post(
        _order_cancel_path(order_id),
        json={
            "reason": "Duplicate order",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["status"] == "cancelled"
    assert data["notes"] == "Original note\nCancelled: Duplicate order"


def test_cancel_order_returns_404_for_missing_order(client: TestClient) -> None:
    response = client.post(
        _order_cancel_path("ord_missing"),
        json={
            "reason": "Missing order",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found: ord_missing"


def test_mark_order_exported(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    response = client.post(_order_export_path(order_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["status"] == "exported"


def test_mark_order_exported_rejects_cancelled_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    cancel_response = client.post(
        _order_cancel_path(order_id),
        json={
            "reason": "Do not send",
        },
    )

    assert cancel_response.status_code == 200

    response = client.post(_order_export_path(order_id))

    assert response.status_code == 400
    assert response.json()["detail"] == f"Cannot export cancelled order: {order_id}"


def test_mark_order_fulfilled(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    response = client.post(_order_fulfill_path(order_id))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order_id
    assert data["status"] == "fulfilled"


def test_mark_order_fulfilled_rejects_cancelled_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    cancel_response = client.post(
        _order_cancel_path(order_id),
        json={
            "reason": "Do not send",
        },
    )

    assert cancel_response.status_code == 200

    response = client.post(_order_fulfill_path(order_id))

    assert response.status_code == 400
    assert response.json()["detail"] == f"Cannot fulfill cancelled order: {order_id}"


def test_delete_order(client: TestClient) -> None:
    store_id = _create_store(client, name="Ithaca Bakery")
    vendor_id = _create_vendor(client, name="Sysco")
    order_id = _create_order(
        client,
        store_id=store_id,
        vendor_id=vendor_id,
    )

    delete_response = client.delete(_order_detail_path(order_id))

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(_order_detail_path(order_id))

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == f"Order not found: {order_id}"


def test_delete_order_returns_404_for_missing_order(client: TestClient) -> None:
    response = client.delete(_order_detail_path("ord_missing"))

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found: ord_missing"


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
    order_date: str = "2026-06-02",
    delivery_date: str | None = None,
    notes: str = "Manual test order",
) -> str:
    payload = {
        "store_id": store_id,
        "vendor_id": vendor_id,
        "order_date": order_date,
        "delivery_date": delivery_date,
        "notes": notes,
        "lines": [
            {
                "source_item_name": "Malt Barrel",
                "source_vendor_sku": "SYS-MALT",
                "quantity": "2",
                "unit": "case",
                "notes": "Need for weekend prep",
            }
        ],
    }

    response = client.post(
        ORDERS_PATH,
        json=payload,
    )

    assert response.status_code == 201

    return response.json()["id"]


def _order_detail_path(order_id: str) -> str:
    return f"{ORDERS_PATH}/{order_id}"


def _order_notes_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/notes"


def _order_cancel_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/cancel"


def _order_export_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/export"


def _order_fulfill_path(order_id: str) -> str:
    return f"{_order_detail_path(order_id)}/fulfill"


def _parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)