from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

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


def seed_store_and_vendor(db_session) -> tuple[Store, Vendor]:
    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)

    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores.save(store)
    vendors.save(vendor)

    return store, vendor


def seed_item_and_vendor_info(db_session, vendor: Vendor) -> tuple[Item, ItemVendorInfo]:
    items = SqlItemRepository(db_session)
    item_vendor_infos = SqlItemVendorInfoRepository(db_session)

    item = Item(
        id="itm_TEST",
        name="Smoke Test Item",
        count_unit="each",
    )

    item_vendor_info = ItemVendorInfo(
        id="ivi_TEST",
        item_id=item.id,
        vendor_id=vendor.id,
        vendor_sku="SMOKE-001",
        price=Decimal("2.50"),
    )

    items.save(item)
    item_vendor_infos.save(item_vendor_info)

    return item, item_vendor_info


def make_pending_order(*, store: Store, vendor: Vendor) -> Order:
    return Order(
        id="ord_TEST",
        store_id=store.id,
        vendor_id=vendor.id,
        order_date=date(2026, 5, 26),
        source="test",
        source_reference="test_order_repository",
        lines=(
            OrderLine(
                id="orl_TEST_1",
                order_id="ord_TEST",
                source_item_name="Smoke Test Item",
                quantity=Decimal("12"),
                unit="each",
                status=OrderLineStatus.PENDING,
            ),
        ),
    )


def test_order_repository_saves_and_loads_order_with_lines(db_session):
    store, vendor = seed_store_and_vendor(db_session)

    order = make_pending_order(store=store, vendor=vendor)

    orders = SqlOrderRepository(db_session)
    orders.save(order)
    db_session.commit()

    saved = orders.get_by_id("ord_TEST")

    assert saved is not None
    assert saved.id == "ord_TEST"
    assert saved.store_id == store.id
    assert saved.vendor_id == vendor.id
    assert saved.order_date == date(2026, 5, 26)
    assert saved.status == OrderStatus.PENDING
    assert len(saved.lines) == 1

    saved_line = saved.lines[0]

    assert saved_line.id == "orl_TEST_1"
    assert saved_line.order_id == "ord_TEST"
    assert saved_line.source_item_name == "Smoke Test Item"
    assert saved_line.quantity == Decimal("12.000")
    assert saved_line.unit == "each"
    assert saved_line.status == OrderLineStatus.PENDING


def test_order_repository_updates_order_and_lines(db_session):
    store, vendor = seed_store_and_vendor(db_session)
    item, item_vendor_info = seed_item_and_vendor_info(db_session, vendor)

    orders = SqlOrderRepository(db_session)

    original = make_pending_order(store=store, vendor=vendor)

    orders.save(original)
    db_session.commit()

    updated_line = replace(
        original.lines[0],
        item_id=item.id,
        item_vendor_info_id=item_vendor_info.id,
        item_name_snapshot=item.name,
        vendor_sku_snapshot=item_vendor_info.vendor_sku,
        unit_price_snapshot=item_vendor_info.price,
        status=OrderLineStatus.PROCESSED,
    )

    updated = replace(
        original,
        status=OrderStatus.PROCESSED,
        lines=(updated_line,),
    )

    orders.save(updated)
    db_session.commit()

    saved = orders.get_by_id("ord_TEST")

    assert saved is not None
    assert saved.status == OrderStatus.PROCESSED
    assert len(saved.lines) == 1

    saved_line = saved.lines[0]

    assert saved_line.status == OrderLineStatus.PROCESSED
    assert saved_line.item_id == item.id
    assert saved_line.item_vendor_info_id == item_vendor_info.id
    assert saved_line.item_name_snapshot == item.name
    assert saved_line.vendor_sku_snapshot == item_vendor_info.vendor_sku
    assert saved_line.unit_price_snapshot == Decimal("2.50")


def test_order_repository_lists_by_store_vendor_and_date(db_session):
    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)

    store = Store(id="str_TEST", name="Bakery")
    other_store = Store(id="str_OTHER", name="Triphammer")

    vendor = Vendor(id="ven_TEST", name="Russo Produce")
    other_vendor = Vendor(id="ven_OTHER", name="Hill & Markes")

    stores.save(store)
    stores.save(other_store)
    vendors.save(vendor)
    vendors.save(other_vendor)

    orders = SqlOrderRepository(db_session)

    orders.save(
        Order(
            id="ord_1",
            store_id=store.id,
            vendor_id=vendor.id,
            order_date=date(2026, 5, 20),
        )
    )
    orders.save(
        Order(
            id="ord_2",
            store_id=store.id,
            vendor_id=vendor.id,
            order_date=date(2026, 5, 26),
        )
    )
    orders.save(
        Order(
            id="ord_3",
            store_id=other_store.id,
            vendor_id=vendor.id,
            order_date=date(2026, 5, 26),
        )
    )
    orders.save(
        Order(
            id="ord_4",
            store_id=store.id,
            vendor_id=other_vendor.id,
            order_date=date(2026, 5, 26),
        )
    )

    db_session.commit()

    matching = orders.list_by_store_and_vendor(
        store.id,
        vendor.id,
        start_date=date(2026, 5, 21),
        end_date=date(2026, 5, 26),
    )

    assert [order.id for order in matching] == ["ord_2"]