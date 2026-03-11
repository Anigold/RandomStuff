"""
Tests for backend.app.services.services_order.

Focus: behavior of OrderServices (app-level orchestration),
ensuring it delegates correctly to the repository and handles errors.
"""

import pytest
from backend.domain.models import Order, OrderItem


def make_order(vendor="Sysco", store="Bakery", date="2025-10-20"):
    return Order(
        vendor=vendor,
        store=store,
        date=date,
        items=[OrderItem("123", "Flour", 2, 10.0, 20.0)],
    )


# ---------------------------------------------------------------------
# get_orders()
# ---------------------------------------------------------------------
def test_get_orders_returns_expected_list(order_services, mock_order_repo):
    expected = [make_order("Sysco", "Bakery")]
    mock_order_repo.list_by_vendor.return_value = expected

    result = order_services.get_orders(["Sysco"], ["Bakery"])
    assert result == expected
    mock_order_repo.list_by_vendor.assert_called_once_with("Sysco")


def test_get_orders_handles_empty_list(order_services, mock_order_repo):
    mock_order_repo.list_by_vendor.return_value = []
    result = order_services.get_orders(["Sysco"], ["Bakery"])
    assert result == []
    mock_order_repo.list_by_vendor.assert_called_once()


# ---------------------------------------------------------------------
# generate_vendor_uploads()
# ---------------------------------------------------------------------
def test_generate_vendor_uploads_delegates_to_repo(order_services, mock_order_repo):
    orders = [make_order()]
    context_map = {orders[0]: {"store": "Bakery", "vendor_info": {}, "date_str": "2025-10-20"}}

    mock_order_repo.generate_vendor_uploads.return_value = ["fake_upload.xlsx"]

    result = order_services.generate_vendor_uploads(
        stores=["Bakery"],
        vendors=["Sysco"],
        start_date="2025-10-01",
        end_date="2025-10-20",
        context_map=context_map,
    )

    mock_order_repo.generate_vendor_uploads.assert_called_once()
    assert result == ["fake_upload.xlsx"]


# ---------------------------------------------------------------------
# archive_order_file()
# ---------------------------------------------------------------------
def test_archive_order_file_logs_warning_on_failure(order_services, mock_order_repo, caplog):
    order = make_order()
    mock_order_repo.archive_order_file.side_effect = Exception("Failed to archive")

    order_services.archive_order_file(order)

    assert "archive" in caplog.text.lower()
    mock_order_repo.archive_order_file.assert_called_once_with(order)


# ---------------------------------------------------------------------
# combine_orders()
# ---------------------------------------------------------------------
def test_combine_orders_calls_repo(order_services, mock_order_repo):
    order_services.combine_orders(["Sysco"])
    mock_order_repo.combine_orders.assert_called_once_with(["Sysco"])
