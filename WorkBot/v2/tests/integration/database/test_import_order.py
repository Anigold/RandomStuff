from __future__ import annotations

from datetime import date
from decimal import Decimal

from workbot_core.application.dto.order_import_row import (
    OrderImportRow,
    OrderLineImportRow,
)
from workbot_core.application.use_cases.import_order import ImportOrder
from workbot_core.domain.models.order import OrderStatus
from workbot_core.domain.models.order_line import OrderLineStatus
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.infrastructure.database.repositories.order_repository import (
    SqlOrderRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


def test_import_order_creates_pending_order_with_pending_lines(db_session):
    
    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)
    orders = SqlOrderRepository(db_session)

    stores.save(store)
    vendors.save(vendor)
    db_session.commit()

    row = OrderImportRow(
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        delivery_date=date(2026, 5, 27),
        source="test",
        source_reference="test_import_order",
        lines=(
            OrderLineImportRow(
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    use_case = ImportOrder(
        orders=orders,
        stores=stores,
        vendors=vendors,
    )

    result = use_case.run(row)
    db_session.commit()

    assert not result.has_errors
    assert result.created is True
    assert result.order_id is not None

    saved = orders.get_by_id(result.order_id)

    assert saved is not None
    assert saved.store_id == store.id
    assert saved.vendor_id == vendor.id
    assert saved.order_date == date(2026, 5, 26)
    assert saved.delivery_date == date(2026, 5, 27)
    assert saved.status == OrderStatus.PENDING
    assert saved.source == "test"
    assert saved.source_reference == "test_import_order"

    assert len(saved.lines) == 1

    line = saved.lines[0]

    assert line.order_id == saved.id
    assert line.source_item_name == "Smoke Test Item"
    assert line.quantity == Decimal("12.000")
    assert line.unit == "each"
    assert line.status == OrderLineStatus.PENDING


def test_import_order_fails_when_store_missing(db_session):

    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    vendors = SqlVendorRepository(db_session)
    vendors.save(vendor)
    db_session.commit()

    row = OrderImportRow(
        store_id="str_MISSING",
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        lines=(
            OrderLineImportRow(
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    use_case = ImportOrder(
        orders=SqlOrderRepository(db_session),
        stores=SqlStoreRepository(db_session),
        vendors=vendors,
    )

    result = use_case.run(row)

    assert result.has_errors
    assert "Store not found: str_MISSING" in result.errors


def test_import_order_fails_when_vendor_missing(db_session):

    store = Store(id="str_TEST", name="Bakery")

    stores = SqlStoreRepository(db_session)
    stores.save(store)
    db_session.commit()

    row = OrderImportRow(
        store_id=store.id,
        vendor_id="ven_MISSING",
        order_date=date(2026, 5, 26),
        lines=(
            OrderLineImportRow(
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    use_case = ImportOrder(
        orders=SqlOrderRepository(db_session),
        stores=stores,
        vendors=SqlVendorRepository(db_session),
    )

    result = use_case.run(row)

    assert result.has_errors
    assert "Vendor not found: ven_MISSING" in result.errors


def test_import_order_fails_when_no_lines(db_session):

    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)

    stores.save(store)
    vendors.save(vendor)
    db_session.commit()

    row = OrderImportRow(
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        lines=(),
    )

    use_case = ImportOrder(
        orders=SqlOrderRepository(db_session),
        stores=stores,
        vendors=vendors,
    )

    result = use_case.run(row)

    assert result.has_errors
    assert "Order must contain at least one line." in result.errors


def test_import_order_does_not_create_duplicate_for_same_source_reference(db_session):
    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)
    orders = SqlOrderRepository(db_session)

    stores.save(store)
    vendors.save(vendor)
    db_session.commit()

    row = OrderImportRow(
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        source="craftable",
        source_reference="same-file-hash",
        lines=(
            OrderLineImportRow(
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    use_case = ImportOrder(
        orders=orders,
        stores=stores,
        vendors=vendors,
    )

    first_result = use_case.run(row)
    db_session.commit()

    second_result = use_case.run(row)
    db_session.commit()

    assert not first_result.has_errors
    assert first_result.created is True
    assert first_result.already_exists is False
    assert first_result.order_id is not None

    assert not second_result.has_errors
    assert second_result.created is False
    assert second_result.already_exists is True
    assert second_result.order_id == first_result.order_id

    all_orders = orders.list_all()

    assert len(all_orders) == 1