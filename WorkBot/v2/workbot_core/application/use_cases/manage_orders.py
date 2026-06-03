from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

from workbot_core.application.dto.order_commands import (
    CancelOrderCommand,
    CreateOrderCommand,
    CreateOrderLineCommand,
    UpdateOrderNotesCommand,
)
from workbot_core.application.interfaces.repositories import (
    OrderRepository,
    StoreRepository,
    VendorRepository,
)
from workbot_core.domain.models.order import Order, OrderStatus
from workbot_core.domain.models.order_line import OrderLine, OrderLineStatus
from workbot_core.utils.ids import IdGenerator


class ManageOrders:
    def __init__(
        self,
        *,
        orders: OrderRepository,
        stores: StoreRepository | None = None,
        vendors: VendorRepository | None = None,
    ) -> None:
        self._orders = orders
        self._stores = stores
        self._vendors = vendors

    def create_order(self, command: CreateOrderCommand) -> Order:
        self._validate_store_exists(command.store_id)
        self._validate_vendor_exists(command.vendor_id)

        if not command.lines:
            raise ValueError("Order must contain at least one line.")

        now = self._now()
        order_id = IdGenerator.order_id()

        order = Order(
            id=order_id,
            store_id=command.store_id,
            vendor_id=command.vendor_id,
            order_date=command.order_date,
            delivery_date=command.delivery_date,
            status=command.status,
            source=self._clean_optional(command.source),
            source_reference=self._clean_optional(command.source_reference),
            notes=self._clean_text(command.notes),
            lines=tuple(
                self._create_order_line(
                    order_id=order_id,
                    command=line_command,
                    created_at=now,
                    updated_at=now,
                )
                for line_command in command.lines
            ),
            created_at=now,
            updated_at=now,
        )

        self._orders.save(order)

        return order

    def list_orders(
        self,
        *,
        store: str | None = None,
        vendor: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Order]:
        store_id = self._resolve_store_id(store)
        vendor_id = self._resolve_vendor_id(vendor)

        if store_id and vendor_id:
            return self._orders.list_by_store_and_vendor(
                store_id,
                vendor_id,
                start_date=start_date,
                end_date=end_date,
            )

        if store_id:
            return self._orders.list_by_store(
                store_id,
                start_date=start_date,
                end_date=end_date,
            )

        if vendor_id:
            return self._orders.list_by_vendor(
                vendor_id,
                start_date=start_date,
                end_date=end_date,
            )

        return self._orders.list_all()

    def get_order(self, order_id: str) -> Order:
        order = self._orders.get_by_id(order_id)

        if order is None:
            raise ValueError(f"Order not found: {order_id}")

        return order

    def update_notes(self, command: UpdateOrderNotesCommand) -> Order:
        order = self.get_order(command.order_id)

        updated = replace(
            order,
            notes=self._clean_text(command.notes),
            updated_at=self._now(),
        )

        self._orders.save(updated)

        return updated

    def cancel_order(self, command: CancelOrderCommand) -> Order:
        order = self.get_order(command.order_id)

        if order.status == OrderStatus.FULFILLED:
            raise ValueError(f"Cannot cancel fulfilled order: {command.order_id}")

        if order.status == OrderStatus.CANCELLED:
            return order

        updated = replace(
            order,
            status=OrderStatus.CANCELLED,
            notes=self._append_note(
                existing=order.notes,
                note=command.reason,
                prefix="Cancelled",
            ),
            updated_at=self._now(),
        )

        self._orders.save(updated)

        return updated

    def mark_exported(self, order_id: str) -> Order:
        order = self.get_order(order_id)

        if order.status == OrderStatus.CANCELLED:
            raise ValueError(f"Cannot export cancelled order: {order_id}")

        if order.status == OrderStatus.ERROR:
            raise ValueError(f"Cannot export errored order: {order_id}")

        updated = replace(
            order,
            status=OrderStatus.EXPORTED,
            updated_at=self._now(),
        )

        self._orders.save(updated)

        return updated

    def mark_fulfilled(self, order_id: str) -> Order:
        order = self.get_order(order_id)

        if order.status == OrderStatus.CANCELLED:
            raise ValueError(f"Cannot fulfill cancelled order: {order_id}")

        if order.status == OrderStatus.ERROR:
            raise ValueError(f"Cannot fulfill errored order: {order_id}")

        updated = replace(
            order,
            status=OrderStatus.FULFILLED,
            updated_at=self._now(),
        )

        self._orders.save(updated)

        return updated

    def delete_order(self, order_id: str) -> None:
        order = self._orders.get_by_id(order_id)

        if order is None:
            raise ValueError(f"Order not found: {order_id}")

        self._orders.delete(order_id)

    def _create_order_line(
        self,
        *,
        order_id: str,
        command: CreateOrderLineCommand,
        created_at: datetime,
        updated_at: datetime,
    ) -> OrderLine:
        return OrderLine(
            id=IdGenerator.order_line_id(),
            order_id=order_id,
            item_id=self._clean_optional(command.item_id),
            item_vendor_info_id=self._clean_optional(command.item_vendor_info_id),
            source_item_name=self._clean_optional(command.source_item_name),
            source_vendor_sku=self._clean_optional(command.source_vendor_sku),
            item_name_snapshot=self._clean_optional(command.item_name_snapshot),
            vendor_sku_snapshot=self._clean_optional(command.vendor_sku_snapshot),
            unit_price_snapshot=command.unit_price_snapshot,
            quantity=command.quantity,
            unit=self._clean_optional(command.unit),
            status=OrderLineStatus.PENDING,
            notes=self._clean_text(command.notes),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _validate_store_exists(self, store_id: str) -> None:
        if self._stores is None:
            raise ValueError("Store repository is required to create orders.")

        if self._stores.get_by_id(store_id) is None:
            raise ValueError(f"Store not found: {store_id}")

    def _validate_vendor_exists(self, vendor_id: str) -> None:
        if self._vendors is None:
            raise ValueError("Vendor repository is required to create orders.")

        if self._vendors.get_by_id(vendor_id) is None:
            raise ValueError(f"Vendor not found: {vendor_id}")

    def _resolve_store_id(self, store: str | None) -> str | None:
        if store is None:
            return None

        if self._stores is None:
            raise ValueError("Store repository is required to filter orders by store.")

        store_name = self._required_text(store, "store")
        store_obj = self._stores.get_by_name(store_name)

        if store_obj is None:
            raise ValueError(f"Store not found: {store_name}")

        return store_obj.id

    def _resolve_vendor_id(self, vendor: str | None) -> str | None:
        if vendor is None:
            return None

        if self._vendors is None:
            raise ValueError("Vendor repository is required to filter orders by vendor.")

        vendor_name = self._required_text(vendor, "vendor")
        vendor_obj = self._vendors.get_by_name(vendor_name)

        if vendor_obj is None:
            raise ValueError(f"Vendor not found: {vendor_name}")

        return vendor_obj.id

    @staticmethod
    def _append_note(
        *,
        existing: str | None,
        note: str | None,
        prefix: str,
    ) -> str:
        cleaned_note = ManageOrders._clean_optional(note)

        if cleaned_note is None:
            return existing or ""

        appended = f"{prefix}: {cleaned_note}"

        if not existing:
            return appended

        return f"{existing}\n{appended}"

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

    @staticmethod
    def _clean_text(value: str | None) -> str:
        if value is None:
            return ""

        return value.strip()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)