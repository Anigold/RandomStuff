from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from tests.fakes.repositories import (
    FakeStoreRepository,
    FakeVendorRepository,
    FakeOrderRepository
)
from workbot_core.application.dto.order_commands import (
    CancelOrderCommand,
    CreateOrderCommand,
    CreateOrderLineCommand,
    UpdateOrderNotesCommand,
)
from workbot_core.application.use_cases.manage_orders import ManageOrders
from workbot_core.domain.models.order import Order, OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor


def test_create_order_saves_new_order() -> None:
    store = Store(id="str_existing", name="Ithaca Bakery")
    vendor = Vendor(id="ven_existing", name="Sysco")

    orders = FakeOrderRepository()
    use_case = ManageOrders(
        orders=orders,
        stores=FakeStoreRepository([store]),
        vendors=FakeVendorRepository([vendor]),
    )

    order = use_case.create_order(
        CreateOrderCommand(
            store_id="str_existing",
            vendor_id="ven_existing",
            order_date=date(2026, 6, 2),
            delivery_date=date(2026, 6, 4),
            notes="Manual order",
            lines=(
                CreateOrderLineCommand(
                    source_item_name="Malt Barrel",
                    source_vendor_sku="SYS-MALT",
                    quantity=Decimal("2"),
                    unit="case",
                    notes="Needed for weekend prep",
                ),
            ),
        )
    )

    saved = orders.get_by_id(order.id)

    assert saved == order
    assert order.id
    assert order.store_id == "str_existing"
    assert order.vendor_id == "ven_existing"
    assert order.order_date == date(2026, 6, 2)
    assert order.delivery_date == date(2026, 6, 4)
    assert order.status == OrderStatus.PENDING
    assert order.notes == "Manual order"
    assert isinstance(order.created_at, datetime)
    assert isinstance(order.updated_at, datetime)

    assert len(order.lines) == 1

    line = order.lines[0]

    assert line.id
    assert line.order_id == order.id
    assert line.source_item_name == "Malt Barrel"
    assert line.source_vendor_sku == "SYS-MALT"
    assert line.quantity == Decimal("2")
    assert line.unit == "case"
    assert line.status == OrderLineStatus.PENDING
    assert line.notes == "Needed for weekend prep"
    assert isinstance(line.created_at, datetime)
    assert isinstance(line.updated_at, datetime)


def test_create_order_cleans_text_fields() -> None:
    store = Store(id="str_existing", name="Ithaca Bakery")
    vendor = Vendor(id="ven_existing", name="Sysco")

    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        stores=FakeStoreRepository([store]),
        vendors=FakeVendorRepository([vendor]),
    )

    order = use_case.create_order(
        CreateOrderCommand(
            store_id="str_existing",
            vendor_id="ven_existing",
            order_date=date(2026, 6, 2),
            source="  manual  ",
            source_reference="  ref-123  ",
            notes="  Manual order  ",
            lines=(
                CreateOrderLineCommand(
                    source_item_name="  Malt Barrel  ",
                    source_vendor_sku="  SYS-MALT  ",
                    quantity=Decimal("2"),
                    unit="  case  ",
                    notes="  Line notes  ",
                ),
            ),
        )
    )

    assert order.source == "manual"
    assert order.source_reference == "ref-123"
    assert order.notes == "Manual order"

    line = order.lines[0]

    assert line.source_item_name == "Malt Barrel"
    assert line.source_vendor_sku == "SYS-MALT"
    assert line.unit == "case"
    assert line.notes == "Line notes"


def test_create_order_rejects_missing_store() -> None:
    vendor = Vendor(id="ven_existing", name="Sysco")

    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        stores=FakeStoreRepository(),
        vendors=FakeVendorRepository([vendor]),
    )

    with pytest.raises(ValueError, match="Store not found: str_missing"):
        use_case.create_order(
            CreateOrderCommand(
                store_id="str_missing",
                vendor_id="ven_existing",
                order_date=date(2026, 6, 2),
                lines=(
                    CreateOrderLineCommand(
                        source_item_name="Malt Barrel",
                        quantity=Decimal("2"),
                    ),
                ),
            )
        )


def test_create_order_rejects_missing_vendor() -> None:
    store = Store(id="str_existing", name="Ithaca Bakery")

    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        stores=FakeStoreRepository([store]),
        vendors=FakeVendorRepository(),
    )

    with pytest.raises(ValueError, match="Vendor not found: ven_missing"):
        use_case.create_order(
            CreateOrderCommand(
                store_id="str_existing",
                vendor_id="ven_missing",
                order_date=date(2026, 6, 2),
                lines=(
                    CreateOrderLineCommand(
                        source_item_name="Malt Barrel",
                        quantity=Decimal("2"),
                    ),
                ),
            )
        )


def test_create_order_rejects_empty_lines() -> None:
    store = Store(id="str_existing", name="Ithaca Bakery")
    vendor = Vendor(id="ven_existing", name="Sysco")

    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        stores=FakeStoreRepository([store]),
        vendors=FakeVendorRepository([vendor]),
    )

    with pytest.raises(ValueError, match="Order must contain at least one line."):
        use_case.create_order(
            CreateOrderCommand(
                store_id="str_existing",
                vendor_id="ven_existing",
                order_date=date(2026, 6, 2),
                lines=(),
            )
        )


def test_list_orders_returns_all_orders_without_filters() -> None:
    first = _order(
        id="ord_first",
        store_id="str_ithaca",
        vendor_id="ven_sysco",
        order_date=date(2026, 6, 1),
    )
    second = _order(
        id="ord_second",
        store_id="str_collegetown",
        vendor_id="ven_regional",
        order_date=date(2026, 6, 2),
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([first, second]),
    )

    result = use_case.list_orders()

    assert result == [first, second]


def test_list_orders_can_filter_by_store_name() -> None:
    ithaca = Store(id="str_ithaca", name="Ithaca Bakery")
    collegetown = Store(id="str_collegetown", name="Collegetown Bagels")

    first = _order(
        id="ord_first",
        store_id="str_ithaca",
        vendor_id="ven_sysco",
        order_date=date(2026, 6, 1),
    )
    second = _order(
        id="ord_second",
        store_id="str_collegetown",
        vendor_id="ven_sysco",
        order_date=date(2026, 6, 2),
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([first, second]),
        stores=FakeStoreRepository([ithaca, collegetown]),
    )

    result = use_case.list_orders(store="Ithaca Bakery")

    assert result == [first]


def test_list_orders_can_filter_by_vendor_name() -> None:
    sysco = Vendor(id="ven_sysco", name="Sysco")
    regional = Vendor(id="ven_regional", name="Regional Produce")

    first = _order(
        id="ord_first",
        store_id="str_ithaca",
        vendor_id="ven_sysco",
        order_date=date(2026, 6, 1),
    )
    second = _order(
        id="ord_second",
        store_id="str_ithaca",
        vendor_id="ven_regional",
        order_date=date(2026, 6, 2),
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([first, second]),
        vendors=FakeVendorRepository([sysco, regional]),
    )

    result = use_case.list_orders(vendor="Sysco")

    assert result == [first]


def test_list_orders_can_filter_by_store_vendor_and_date_range() -> None:
    store = Store(id="str_ithaca", name="Ithaca Bakery")
    vendor = Vendor(id="ven_sysco", name="Sysco")

    included = _order(
        id="ord_included",
        store_id="str_ithaca",
        vendor_id="ven_sysco",
        order_date=date(2026, 6, 2),
    )
    wrong_date = _order(
        id="ord_wrong_date",
        store_id="str_ithaca",
        vendor_id="ven_sysco",
        order_date=date(2026, 5, 1),
    )
    wrong_vendor = _order(
        id="ord_wrong_vendor",
        store_id="str_ithaca",
        vendor_id="ven_other",
        order_date=date(2026, 6, 2),
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([included, wrong_date, wrong_vendor]),
        stores=FakeStoreRepository([store]),
        vendors=FakeVendorRepository([vendor]),
    )

    result = use_case.list_orders(
        store="Ithaca Bakery",
        vendor="Sysco",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 30),
    )

    assert result == [included]


def test_list_orders_rejects_missing_store_filter() -> None:
    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        stores=FakeStoreRepository(),
    )

    with pytest.raises(ValueError, match="Store not found: Missing Store"):
        use_case.list_orders(store="Missing Store")


def test_list_orders_rejects_missing_vendor_filter() -> None:
    use_case = ManageOrders(
        orders=FakeOrderRepository(),
        vendors=FakeVendorRepository(),
    )

    with pytest.raises(ValueError, match="Vendor not found: Missing Vendor"):
        use_case.list_orders(vendor="Missing Vendor")


def test_get_order_returns_existing_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    result = use_case.get_order("ord_existing")

    assert result == order


def test_get_order_rejects_missing_order() -> None:
    use_case = ManageOrders(
        orders=FakeOrderRepository(),
    )

    with pytest.raises(ValueError, match="Order not found: ord_missing"):
        use_case.get_order("ord_missing")


def test_update_notes_saves_updated_notes() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        notes="Old notes",
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    updated = use_case.update_notes(
        UpdateOrderNotesCommand(
            order_id="ord_existing",
            notes="Updated notes",
        )
    )

    saved = orders.get_by_id("ord_existing")

    assert saved == updated
    assert updated.id == "ord_existing"
    assert updated.notes == "Updated notes"
    assert updated.created_at == order.created_at
    assert updated.updated_at != order.updated_at


def test_cancel_order_sets_status_cancelled_and_appends_reason() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.PROCESSED,
        notes="Original note",
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    cancelled = use_case.cancel_order(
        CancelOrderCommand(
            order_id="ord_existing",
            reason="Duplicate order",
        )
    )

    saved = orders.get_by_id("ord_existing")

    assert saved == cancelled
    assert cancelled.status == OrderStatus.CANCELLED
    assert cancelled.notes == "Original note\nCancelled: Duplicate order"
    assert cancelled.created_at == order.created_at
    assert cancelled.updated_at != order.updated_at


def test_cancel_order_without_reason_does_not_change_notes() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.PROCESSED,
        notes="Original note",
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    cancelled = use_case.cancel_order(
        CancelOrderCommand(
            order_id="ord_existing",
            reason=None,
        )
    )

    assert cancelled.status == OrderStatus.CANCELLED
    assert cancelled.notes == "Original note"


def test_cancel_order_returns_existing_cancelled_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.CANCELLED,
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    result = use_case.cancel_order(
        CancelOrderCommand(
            order_id="ord_existing",
            reason="Already cancelled",
        )
    )

    assert result == order


def test_cancel_order_rejects_fulfilled_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.FULFILLED,
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    with pytest.raises(
        ValueError,
        match="Cannot cancel fulfilled order: ord_existing",
    ):
        use_case.cancel_order(
            CancelOrderCommand(
                order_id="ord_existing",
                reason="Mistake",
            )
        )


def test_mark_exported_sets_status_exported() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.PROCESSED,
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    exported = use_case.mark_exported("ord_existing")

    saved = orders.get_by_id("ord_existing")

    assert saved == exported
    assert exported.status == OrderStatus.EXPORTED
    assert exported.created_at == order.created_at
    assert exported.updated_at != order.updated_at


def test_mark_exported_rejects_cancelled_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.CANCELLED,
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    with pytest.raises(
        ValueError,
        match="Cannot export cancelled order: ord_existing",
    ):
        use_case.mark_exported("ord_existing")


def test_mark_exported_rejects_errored_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.ERROR,
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    with pytest.raises(
        ValueError,
        match="Cannot export errored order: ord_existing",
    ):
        use_case.mark_exported("ord_existing")


def test_mark_fulfilled_sets_status_fulfilled() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.EXPORTED,
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    fulfilled = use_case.mark_fulfilled("ord_existing")

    saved = orders.get_by_id("ord_existing")

    assert saved == fulfilled
    assert fulfilled.status == OrderStatus.FULFILLED
    assert fulfilled.created_at == order.created_at
    assert fulfilled.updated_at != order.updated_at


def test_mark_fulfilled_rejects_cancelled_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.CANCELLED,
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    with pytest.raises(
        ValueError,
        match="Cannot fulfill cancelled order: ord_existing",
    ):
        use_case.mark_fulfilled("ord_existing")


def test_mark_fulfilled_rejects_errored_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
        status=OrderStatus.ERROR,
    )

    use_case = ManageOrders(
        orders=FakeOrderRepository([order]),
    )

    with pytest.raises(
        ValueError,
        match="Cannot fulfill errored order: ord_existing",
    ):
        use_case.mark_fulfilled("ord_existing")


def test_delete_order_removes_existing_order() -> None:
    order = _order(
        id="ord_existing",
        store_id="str_existing",
        vendor_id="ven_existing",
    )

    orders = FakeOrderRepository([order])
    use_case = ManageOrders(orders=orders)

    use_case.delete_order("ord_existing")

    assert orders.get_by_id("ord_existing") is None


def test_delete_order_rejects_missing_order() -> None:
    use_case = ManageOrders(
        orders=FakeOrderRepository(),
    )

    with pytest.raises(ValueError, match="Order not found: ord_missing"):
        use_case.delete_order("ord_missing")


def _date_is_in_range(
    value: date,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> bool:
    if start_date is not None and value < start_date:
        return False

    if end_date is not None and value > end_date:
        return False

    return True


def _order(
    *,
    id: str,
    store_id: str,
    vendor_id: str,
    order_date: date = date(2026, 6, 2),
    delivery_date: date | None = None,
    status: OrderStatus = OrderStatus.PENDING,
    source: str | None = None,
    source_reference: str | None = None,
    notes: str | None = "",
    lines: tuple[OrderLine, ...] | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> Order:
    created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    updated_at = updated_at or datetime(2026, 1, 1, 12, 0, 0)

    return Order(
        id=id,
        store_id=store_id,
        vendor_id=vendor_id,
        order_date=order_date,
        delivery_date=delivery_date,
        status=status,
        source=source,
        source_reference=source_reference,
        notes=notes,
        lines=lines or (
            _order_line(
                id=f"orl_{id}",
                order_id=id,
            ),
        ),
        created_at=created_at,
        updated_at=updated_at,
    )


def _order_line(
    *,
    id: str,
    order_id: str,
    item_id: str | None = None,
    item_vendor_info_id: str | None = None,
    source_item_name: str | None = "Malt Barrel",
    source_vendor_sku: str | None = "SYS-MALT",
    item_name_snapshot: str | None = None,
    vendor_sku_snapshot: str | None = None,
    unit_price_snapshot: Decimal | None = None,
    quantity: Decimal = Decimal("1"),
    unit: str | None = "case",
    status: OrderLineStatus = OrderLineStatus.PENDING,
    status_reason: str | None = None,
    moved_to_order_id: str | None = None,
    notes: str = "",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> OrderLine:
    created_at = created_at or datetime(2026, 1, 1, 12, 0, 0)
    updated_at = updated_at or datetime(2026, 1, 1, 12, 0, 0)

    return OrderLine(
        id=id,
        order_id=order_id,
        item_id=item_id,
        item_vendor_info_id=item_vendor_info_id,
        source_item_name=source_item_name,
        source_vendor_sku=source_vendor_sku,
        item_name_snapshot=item_name_snapshot,
        vendor_sku_snapshot=vendor_sku_snapshot,
        unit_price_snapshot=unit_price_snapshot,
        quantity=quantity,
        unit=unit,
        status=status,
        status_reason=status_reason,
        moved_to_order_id=moved_to_order_id,
        notes=notes,
        created_at=created_at,
        updated_at=updated_at,
    )