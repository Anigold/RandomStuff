from __future__ import annotations

from dataclasses import replace

from workbot_core.application.dto.resolve_order_lines_result import (
    ResolveOrderLinesResult,
    ResolveOrderLinesResultBuilder,
)
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemVendorInfoRepository,
    OrderRepository,
)
from workbot_core.application.services.order_line_resolution_service import (
    OrderLineResolutionService,
)
from workbot_core.domain.models.order import OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus


class ResolveOrderLines:
    def __init__(
        self,
        *,
        orders: OrderRepository,
        items: ItemRepository,
        item_vendor_infos: ItemVendorInfoRepository,
        resolution_service: OrderLineResolutionService | None = None,
    ) -> None:
        self._orders = orders
        self._items = items
        self._item_vendor_infos = item_vendor_infos
        self._resolution_service = resolution_service or OrderLineResolutionService()

    def run(self, order_id: str) -> ResolveOrderLinesResult:
        order = self._orders.get_by_id(order_id)

        if order is None:
            return ResolveOrderLinesResult(
                order_id=order_id,
                errored=1,
                errors=(f"Order not found: {order_id}",),
            )

        result = ResolveOrderLinesResultBuilder(order_id=order.id)

        resolved_lines = tuple(
            self._resolve_line(order=order, line=line, result=result)
            for line in order.lines
        )

        new_status = (
            OrderStatus.ERROR
            if any(line.status == OrderLineStatus.ERROR for line in resolved_lines)
            else OrderStatus.PROCESSED
        )

        updated_order = replace(
            order,
            status=new_status,
            lines=resolved_lines,
        )

        self._orders.save(updated_order)

        return result.build()

    def _resolve_line(
        self,
        *,
        order,
        line: OrderLine,
        result: ResolveOrderLinesResultBuilder,
    ) -> OrderLine:
        if line.status != OrderLineStatus.PENDING:
            result.add_skipped()
            return line

        if not line.source_item_name:
            message = f"Order line {line.id} has no source item name."
            result.add_errored(message)
            return self._resolution_service.errored_line(
                line=line,
                reason=message,
            )

        item = self._items.get_by_name(line.source_item_name)

        if item is None:
            message = f"Item not found for order line {line.id}: {line.source_item_name}"
            result.add_errored(message)
            return self._resolution_service.errored_line(
                line=line,
                reason=message,
            )

        if line.source_vendor_sku:
            vendor_info = self._item_vendor_infos.get_by_item_vendor_sku(
                item_id=item.id,
                vendor_id=order.vendor_id,
                vendor_sku=line.source_vendor_sku,
            )

            if vendor_info is None:
                message = (
                    f"Vendor info not found for order line {line.id}: "
                    f"item={item.name}, vendor_id={order.vendor_id}, "
                    f"sku={line.source_vendor_sku}"
                )
                result.add_errored(message)
                return self._resolution_service.errored_line(
                    line=line,
                    reason=message,
                )

            processed = self._resolution_service.processed_line(
                line=line,
                item=item,
                item_vendor_info=vendor_info,
            )

            result.add_processed()
            return processed

        vendor_infos = self._item_vendor_infos.list_active_for_vendor(order.vendor_id)

        matching_infos = [
            info for info in vendor_infos
            if info.item_id == item.id
        ]

        if not matching_infos:
            message = (
                f"Vendor info not found for order line {line.id}: "
                f"item={item.name}, vendor_id={order.vendor_id}"
            )
            result.add_errored(message)
            return self._resolution_service.errored_line(
                line=line,
                reason=message,
            )

        if len(matching_infos) > 1:
            message = (
                f"Multiple active vendor info records found for order line {line.id}: "
                f"item={item.name}, vendor_id={order.vendor_id}"
            )
            result.add_errored(message)
            return self._resolution_service.errored_line(
                line=line,
                reason=message,
            )

        processed = self._resolution_service.processed_line(
            line=line,
            item=item,
            item_vendor_info=matching_infos[0],
        )

        result.add_processed()
        return processed