from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus


class OrderLineResolutionService:
    def processed_line(
        self,
        *,
        line: OrderLine,
        item: Item,
        item_vendor_info: ItemVendorInfo,
    ) -> OrderLine:
        return replace(
            line,
            item_id=item.id,
            item_vendor_info_id=item_vendor_info.id,
            item_name_snapshot=item.name,
            vendor_sku_snapshot=item_vendor_info.vendor_sku,
            unit_price_snapshot=item_vendor_info.price,
            status=OrderLineStatus.PROCESSED,
            status_reason=None,
            updated_at=datetime.now(UTC),
        )

    def errored_line(self, *, line: OrderLine, reason: str) -> OrderLine:
        return replace(
            line,
            status=OrderLineStatus.ERROR,
            status_reason=reason,
            updated_at=datetime.now(UTC),
        )

    def ignored_line(self, *, line: OrderLine, reason: str) -> OrderLine:
        return replace(
            line,
            status=OrderLineStatus.IGNORED,
            status_reason=reason,
            updated_at=datetime.now(UTC),
        )

    def removed_line(
        self,
        *,
        line: OrderLine,
        reason: str | None = None,
    ) -> OrderLine:
        return replace(
            line,
            status=OrderLineStatus.REMOVED,
            status_reason=reason,
            updated_at=datetime.now(UTC),
        )

    def moved_line(
        self,
        *,
        line: OrderLine,
        moved_to_order_id: str,
        reason: str | None = None,
    ) -> OrderLine:
        return replace(
            line,
            status=OrderLineStatus.MOVED,
            moved_to_order_id=moved_to_order_id,
            status_reason=reason,
            updated_at=datetime.now(UTC),
        )