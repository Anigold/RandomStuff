from __future__ import annotations

from decimal import Decimal

from workbot_core.application.services.order_line_resolution_service import (
    OrderLineResolutionService,
)
from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus


def test_processed_line_returns_replacement_with_snapshots():
    service = OrderLineResolutionService()

    line = OrderLine(
        id="orl_TEST",
        order_id="ord_TEST",
        source_item_name="Smoke Test Item",
        quantity=Decimal("12"),
        unit="each",
    )

    item = Item(
        id="itm_TEST",
        name="Smoke Test Item",
        count_unit="each",
    )

    item_vendor_info = ItemVendorInfo(
        id="ivi_TEST",
        item_id=item.id,
        vendor_id="ven_TEST",
        vendor_sku="SMOKE-001",
        price=Decimal("2.50"),
    )

    processed = service.processed_line(
        line=line,
        item=item,
        item_vendor_info=item_vendor_info,
    )

    assert processed is not line
    assert processed.id == line.id
    assert processed.order_id == line.order_id

    assert processed.item_id == item.id
    assert processed.item_vendor_info_id == item_vendor_info.id
    assert processed.item_name_snapshot == item.name
    assert processed.vendor_sku_snapshot == item_vendor_info.vendor_sku
    assert processed.unit_price_snapshot == item_vendor_info.price
    assert processed.status == OrderLineStatus.PROCESSED
    assert processed.status_reason is None

    assert line.status == OrderLineStatus.PENDING
    assert line.item_id is None


def test_errored_line_returns_replacement_with_reason():
    service = OrderLineResolutionService()

    line = OrderLine(
        id="orl_TEST",
        order_id="ord_TEST",
        source_item_name="Unknown Item",
    )

    errored = service.errored_line(
        line=line,
        reason="Item not found: Unknown Item",
    )

    assert errored is not line
    assert errored.status == OrderLineStatus.ERROR
    assert errored.status_reason == "Item not found: Unknown Item"
    assert line.status == OrderLineStatus.PENDING


def test_ignored_line_returns_replacement_with_reason():
    service = OrderLineResolutionService()

    line = OrderLine(
        id="orl_TEST",
        order_id="ord_TEST",
        source_item_name="Comment Line",
    )

    ignored = service.ignored_line(
        line=line,
        reason="Comment or non-orderable row.",
    )

    assert ignored.status == OrderLineStatus.IGNORED
    assert ignored.status_reason == "Comment or non-orderable row."


def test_removed_line_returns_replacement_with_optional_reason():
    service = OrderLineResolutionService()

    line = OrderLine(
        id="orl_TEST",
        order_id="ord_TEST",
        source_item_name="Smoke Test Item",
    )

    removed = service.removed_line(
        line=line,
        reason="Removed during manual review.",
    )

    assert removed.status == OrderLineStatus.REMOVED
    assert removed.status_reason == "Removed during manual review."


def test_moved_line_returns_replacement_with_target_order():
    service = OrderLineResolutionService()

    line = OrderLine(
        id="orl_TEST",
        order_id="ord_TEST",
        source_item_name="Smoke Test Item",
    )

    moved = service.moved_line(
        line=line,
        moved_to_order_id="ord_OTHER",
        reason="Belongs to different vendor order.",
    )

    assert moved.status == OrderLineStatus.MOVED
    assert moved.moved_to_order_id == "ord_OTHER"
    assert moved.status_reason == "Belongs to different vendor order."