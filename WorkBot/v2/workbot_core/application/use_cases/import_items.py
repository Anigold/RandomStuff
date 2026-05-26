from __future__ import annotations

from collections.abc import Iterable

from workbot_core.application.dto.import_result import ImportResult, ImportResultBuilder
from workbot_core.application.dto.item_import_row import ItemImportRow
from workbot_core.application.interfaces.repositories import (
    ItemRepository,
    ItemStoreInfoRepository,
    ItemVendorInfoRepository,
)
from workbot_core.application.services.item_import_service import ItemImportService


class ImportItems:
    def __init__(
        self,
        *,
        items: ItemRepository,
        item_vendor_infos: ItemVendorInfoRepository,
        item_store_infos: ItemStoreInfoRepository,
        item_import_service: ItemImportService | None = None,
    ) -> None:
        self._items = items
        self._item_vendor_infos = item_vendor_infos
        self._item_store_infos = item_store_infos
        self._service = item_import_service or ItemImportService()

    def run(self, rows: Iterable[ItemImportRow]) -> ImportResult:
        result = ImportResultBuilder()

        for row in rows:
            try:
                self._import_row(row, result)
            except Exception as exc:
                result.add_error(f"{row.id} / {row.name}: {exc}")

        return result.build()

    def _import_row(self, row: ItemImportRow, result: ImportResultBuilder) -> None:
        existing_item = self._items.get_by_id(row.id)

        if existing_item is None:
            existing_item = self._items.get_by_name(row.name)

        if existing_item is None:
            item = self._service.create_item(row)
            self._items.save(item)
            result.add_created()
        else:
            item = self._service.replace_item(existing_item, row)
            self._items.save(item)
            result.add_updated()

        self._save_vendor_info_rows(item.id, row)
        self._save_store_info_rows(item.id, row)

    def _save_vendor_info_rows(self, item_id: str, row: ItemImportRow) -> None:
        for vendor_row in row.vendor_info:
            existing = self._item_vendor_infos.get_by_item_vendor_sku(
                item_id=item_id,
                vendor_id=vendor_row.vendor_id,
                vendor_sku=vendor_row.vendor_sku,
            )

            if existing is None:
                info = self._service.create_item_vendor_info(
                    item_id=item_id,
                    row=vendor_row,
                )
            else:
                info = self._service.replace_item_vendor_info(
                    existing=existing,
                    row=vendor_row,
                )

            self._item_vendor_infos.save(info)

    def _save_store_info_rows(self, item_id: str, row: ItemImportRow) -> None:
        for store_row in row.store_info:
            existing = self._item_store_infos.get_by_item_store(
                item_id=item_id,
                store_id=store_row.store_id,
            )

            if existing is None:
                info = self._service.create_item_store_info(
                    item_id=item_id,
                    row=store_row,
                )
            else:
                info = self._service.replace_item_store_info(
                    existing=existing,
                    row=store_row,
                )

            self._item_store_infos.save(info)