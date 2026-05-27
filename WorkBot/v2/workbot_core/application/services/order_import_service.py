from __future__ import annotations

from workbot_core.application.dto.order_import_row import (
    OrderImportRow,
    OrderLineImportRow,
)
from workbot_core.domain.models.order import Order, OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus
from workbot_core.utils.ids import IdGenerator


class OrderImportService:
    
    """Creates Order domain objects from import DTOs.

    This service does not save anything. It only translates import DTOs into
    passive domain objects with generated IDs.
    """

    def create_order(self, row: OrderImportRow) -> Order:
        order_id = IdGenerator.order_id()

        return Order(
            id=order_id,
            store_id=row.store_id,
            vendor_id=row.vendor_id,
            order_date=row.order_date,
            delivery_date=row.delivery_date,
            status=OrderStatus.PENDING,
            source=self._clean_optional(row.source),
            source_reference=self._clean_optional(row.source_reference),
            notes=row.notes or "",
            lines=tuple(
                self.create_order_line(order_id=order_id, row=line_row)
                for line_row in row.lines
            ),
        )

    def create_order_line(
        self,
        *,
        order_id: str,
        row: OrderLineImportRow,
    ) -> OrderLine:
        return OrderLine(
            id=IdGenerator.order_line_id(),
            order_id=order_id,
            source_item_name=self._required_text(
                row.source_item_name,
                "source item name",
            ),
            source_vendor_sku=self._clean_optional(row.source_vendor_sku),
            quantity=row.quantity,
            unit=self._clean_optional(row.unit),
            unit_price_snapshot=row.unit_price,
            status=OrderLineStatus.PENDING,
            notes=row.notes or "",
        )

    @staticmethod
    def _clean_optional(value: str | None) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()
        return cleaned or None

    @classmethod
    def _required_text(cls, value: str, field_name: str) -> str:
        cleaned = cls._clean_optional(value)

        if cleaned is None:
            raise ValueError(f"{field_name} cannot be empty.")

        return cleaned