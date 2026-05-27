from __future__ import annotations

from datetime import date
from decimal import Decimal

from workbot_core.application.use_cases.resolve_order_lines import ResolveOrderLines
from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.domain.models.order import Order, OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_vendor_info_repository import (
    SqlItemVendorInfoRepository,
)
from workbot_core.infrastructure.database.repositories.order_repository import (
    SqlOrderRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


def test_resolve_order_lines_processes_matching_pending_line(db_session):
    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")
    item = Item(
        id="itm_TEST",
        name="Smoke Test Item",
        count_unit_quantity=Decimal("1"),
        count_unit_measure="each",
    )
    item_vendor_info = ItemVendorInfo(
        id="ivi_TEST",
        item_id=item.id,
        vendor_id=vendor.id,
        vendor_sku="SMOKE-001",
        price=Decimal("2.50"),
        is_active=True,
    )

    SqlStoreRepository(db_session).save(store)
    SqlVendorRepository(db_session).save(vendor)
    SqlItemRepository(db_session).save(item)
    SqlItemVendorInfoRepository(db_session).save(item_vendor_info)

    order = Order(
        id="ord_TEST",
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        lines=(
            OrderLine(
                id="orl_TEST",
                order_id="ord_TEST",
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    orders = SqlOrderRepository(db_session)
    orders.save(order)
    db_session.commit()

    use_case = ResolveOrderLines(
        orders=orders,
        items=SqlItemRepository(db_session),
        item_vendor_infos=SqlItemVendorInfoRepository(db_session),
    )

    result = use_case.run("ord_TEST")
    db_session.commit()

    assert not result.has_errors
    assert result.processed == 1
    assert result.errored == 0

    saved = orders.get_by_id("ord_TEST")

    assert saved is not None
    assert saved.status == OrderStatus.PROCESSED

    line = saved.lines[0]

    assert line.status == OrderLineStatus.PROCESSED
    assert line.item_id == item.id
    assert line.item_vendor_info_id == item_vendor_info.id
    assert line.item_name_snapshot == item.name
    assert line.vendor_sku_snapshot == item_vendor_info.vendor_sku
    assert line.unit_price_snapshot == item_vendor_info.price


def test_resolve_order_lines_marks_missing_item_as_error(db_session):
    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    SqlStoreRepository(db_session).save(store)
    SqlVendorRepository(db_session).save(vendor)

    order = Order(
        id="ord_TEST",
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        lines=(
            OrderLine(
                id="orl_TEST",
                order_id="ord_TEST",
                source_item_name="Missing Item",
                quantity=Decimal("12"),
                unit="each",
            ),
        ),
    )

    orders = SqlOrderRepository(db_session)
    orders.save(order)
    db_session.commit()

    use_case = ResolveOrderLines(
        orders=orders,
        items=SqlItemRepository(db_session),
        item_vendor_infos=SqlItemVendorInfoRepository(db_session),
    )

    result = use_case.run("ord_TEST")
    db_session.commit()

    assert result.has_errors
    assert result.processed == 0
    assert result.errored == 1

    saved = orders.get_by_id("ord_TEST")

    assert saved is not None
    assert saved.status == OrderStatus.ERROR

    line = saved.lines[0]

    assert line.status == OrderLineStatus.ERROR
    assert line.status_reason is not None
    assert "Item not found" in line.status_reason