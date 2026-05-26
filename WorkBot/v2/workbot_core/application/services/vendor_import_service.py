from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from workbot_core.application.dto.vendor_import_row import (
    ContactInfoImportRow,
    OrderingInfoImportRow,
    ScheduleEntryImportRow,
    VendorImportRow,
)
from workbot_core.domain.models.vendor import (
    ContactInfo,
    OrderingInfo,
    ScheduleEntry,
    Vendor,
)
from workbot_core.utils.ids import IdGenerator


class VendorImportService:
    """Creates replacement Vendor objects from vendor import rows."""

    def create_vendor(
        self,
        row: VendorImportRow,
        *,
        store_ids: tuple[str, ...],
    ) -> Vendor:
        return Vendor(
            id=row.id or IdGenerator.vendor_id(),
            name=self._required_text(row.name, "vendor name"),
            order_format=self._clean_text(row.order_format),
            special_notes=self._clean_text(row.special_notes),
            min_order_value=row.min_order_value,
            min_order_cases=row.min_order_cases,
            internal_contacts=self._contacts(row.internal_contacts),
            ordering=self._ordering(row.ordering),
            store_ids=store_ids,
        )

    def replace_vendor(
        self,
        existing: Vendor,
        row: VendorImportRow,
        *,
        store_ids: tuple[str, ...],
    ) -> Vendor:
        return replace(
            existing,
            name=self._required_text(row.name, "vendor name"),
            order_format=self._clean_text(row.order_format),
            special_notes=self._clean_text(row.special_notes),
            min_order_value=row.min_order_value,
            min_order_cases=row.min_order_cases,
            internal_contacts=self._contacts(row.internal_contacts),
            ordering=self._ordering(row.ordering),
            store_ids=store_ids,
        )

    def _contacts(
        self,
        rows: tuple[ContactInfoImportRow, ...],
    ) -> tuple[ContactInfo, ...]:
        contacts: list[ContactInfo] = []

        for row in rows:
            # Skip completely blank contacts from old placeholder JSON.
            if not any((row.name, row.title, row.email, row.phone)):
                continue

            contacts.append(
                ContactInfo(
                    name=self._clean_text(row.name),
                    title=self._clean_text(row.title),
                    email=self._clean_text(row.email),
                    phone=self._clean_text(row.phone),
                )
            )

        return tuple(contacts)

    def _ordering(self, row: OrderingInfoImportRow) -> OrderingInfo:
        return OrderingInfo(
            method=tuple(self._clean_text(method) for method in row.method if method),
            email=self._clean_text(row.email),
            portal_url=self._clean_text(row.portal_url),
            phone_number=self._clean_text(row.phone_number),
            schedule=self._schedule(row.schedule),
        )

    def _schedule(
        self,
        rows: tuple[ScheduleEntryImportRow, ...],
    ) -> tuple[ScheduleEntry, ...]:
        entries: list[ScheduleEntry] = []

        for row in rows:
            if not row.order_day and not row.delivery_days and not row.cutoff_time:
                continue

            entries.append(
                ScheduleEntry(
                    order_day=self._clean_text(row.order_day),
                    delivery_days=tuple(
                        self._clean_text(day)
                        for day in row.delivery_days
                        if day
                    ),
                    cutoff_time=self._clean_text(row.cutoff_time),
                )
            )

        return tuple(entries)

    @staticmethod
    def _clean_text(value: str | None) -> str:
        if value is None:
            return ""

        return value.strip()

    @classmethod
    def _required_text(cls, value: str | None, field_name: str) -> str:
        cleaned = cls._clean_text(value)

        if not cleaned:
            raise ValueError(f"{field_name} cannot be empty.")

        return cleaned