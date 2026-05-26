from __future__ import annotations

from collections.abc import Iterable

from workbot_core.application.dto.import_result import ImportResult, ImportResultBuilder
from workbot_core.application.dto.vendor_import_row import VendorImportRow
from workbot_core.application.interfaces.repositories import StoreRepository, VendorRepository
from workbot_core.application.services.vendor_import_service import VendorImportService


class ImportVendors:
    def __init__(
        self,
        *,
        vendors: VendorRepository,
        stores: StoreRepository,
        vendor_import_service: VendorImportService | None = None,
    ) -> None:
        self._vendors = vendors
        self._stores = stores
        self._service = vendor_import_service or VendorImportService()

    def run(self, rows: Iterable[VendorImportRow]) -> ImportResult:
        result = ImportResultBuilder()

        for row in rows:
            try:
                self._import_row(row, result)
            except Exception as exc:
                result.add_error(f"{row.id or '<no id>'} / {row.name}: {exc}")

        return result.build()

    def _import_row(self, row: VendorImportRow, result: ImportResultBuilder) -> None:
        store_ids = self._resolve_store_ids(row)

        existing = None

        if row.id is not None:
            existing = self._vendors.get_by_id(row.id)

        if existing is None:
            existing = self._vendors.get_by_name(row.name)

        if existing is None:
            vendor = self._service.create_vendor(row, store_ids=store_ids)
            self._vendors.save(vendor)
            result.add_created()
            return

        vendor = self._service.replace_vendor(
            existing,
            row,
            store_ids=store_ids,
        )
        self._vendors.save(vendor)
        result.add_updated()

    def _resolve_store_ids(self, row: VendorImportRow) -> tuple[str, ...]:
        resolved_ids: list[str] = []

        for store_name in row.store_names:
            store = self._stores.get_by_name(store_name)

            if store is None:
                raise ValueError(f"Store not found for vendor {row.name}: {store_name}")

            resolved_ids.append(store.id)

        return tuple(resolved_ids)