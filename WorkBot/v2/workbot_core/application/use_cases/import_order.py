from __future__ import annotations

from workbot_core.application.dto.import_order_result import ImportOrderResult
from workbot_core.application.dto.order_import_row import OrderImportRow
from workbot_core.application.interfaces.repositories import (
    OrderRepository,
    StoreRepository,
    VendorRepository,
)
from workbot_core.application.services.order_import_service import OrderImportService


class ImportOrder:
    def __init__(
        self,
        *,
        orders: OrderRepository,
        stores: StoreRepository,
        vendors: VendorRepository,
        order_import_service: OrderImportService | None = None,
    ) -> None:
        self._orders = orders
        self._stores = stores
        self._vendors = vendors
        self._service = order_import_service or OrderImportService()

    def run(self, row: OrderImportRow) -> ImportOrderResult:
        errors = self._validate_references(row)

        if errors:
            return ImportOrderResult(errors=tuple(errors))

        try:
            order = self._service.create_order(row)
            self._orders.save(order)
        except Exception as exc:
            return ImportOrderResult(errors=(str(exc),))

        return ImportOrderResult(
            order_id=order.id,
            created=True,
        )

    def _validate_references(self, row: OrderImportRow) -> list[str]:
        errors: list[str] = []

        if self._stores.get_by_id(row.store_id) is None:
            errors.append(f"Store not found: {row.store_id}")

        if self._vendors.get_by_id(row.vendor_id) is None:
            errors.append(f"Vendor not found: {row.vendor_id}")

        if not row.lines:
            errors.append("Order must contain at least one line.")

        return errors