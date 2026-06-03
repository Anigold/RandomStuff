from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from workbot_core.application.dto.vendor_commands import (
    CreateVendorCommand,
    UpdateVendorCommand,
)
from workbot_core.application.interfaces.repositories import VendorRepository
from workbot_core.domain.models.vendor import (
    ContactInfo,
    OrderingInfo,
    ScheduleEntry,
    Vendor,
    VendorStoreReference
)
from workbot_core.utils.ids import IdGenerator


class ManageVendors:
    def __init__(
        self,
        *,
        vendors: VendorRepository,
    ) -> None:
        self._vendors = vendors

    def create_vendor(self, command: CreateVendorCommand) -> Vendor:
        existing = self._vendors.get_by_name(command.name)

        if existing is not None:
            raise ValueError(f"Vendor already exists: {command.name}")

        now = self._now()

        vendor = Vendor(
            id=IdGenerator.vendor_id(),
            name=self._required_text(command.name, "vendor name"),
            is_active=command.is_active,
            order_format=self._clean_text(command.order_format),
            special_notes=self._clean_text(command.special_notes),
            min_order_value=command.min_order_value,
            min_order_cases=command.min_order_cases,
            internal_contacts=self._clean_contacts(command.internal_contacts),
            ordering=self._clean_ordering(command.ordering),
            store_references=self._clean_store_references(
                command.store_references
            ),
            created_at=now,
            updated_at=now,
        )

        self._vendors.save(vendor)

        return vendor

    def list_vendors(
        self,
        *,
        search: str | None = None,
        include_inactive: bool = True,
    ) -> list[Vendor]:
        vendors = (
            self._vendors.list_all()
            if include_inactive
            else self._vendors.list_active()
        )

        cleaned_search = self._clean_optional(search)

        if cleaned_search is None:
            return vendors

        search_lower = cleaned_search.casefold()

        return [
            vendor
            for vendor in vendors
            if search_lower in vendor.name.casefold()
        ]


    def get_vendor(self, vendor_id: str) -> Vendor:
        vendor = self._vendors.get_by_id(vendor_id)

        if vendor is None:
            raise ValueError(f"Vendor not found: {vendor_id}")

        return vendor

    def update_vendor(self, command: UpdateVendorCommand) -> Vendor:
        vendor = self._vendors.get_by_id(command.vendor_id)

        if vendor is None:
            raise ValueError(f"Vendor not found: {command.vendor_id}")

        existing = self._vendors.get_by_name(command.name)

        if existing is not None and existing.id != vendor.id:
            raise ValueError(f"Vendor already exists: {command.name}")

        updated = replace(
            vendor,
            name=self._required_text(command.name, "vendor name"),
            is_active=command.is_active,
            order_format=self._clean_text(command.order_format),
            special_notes=self._clean_text(command.special_notes),
            min_order_value=command.min_order_value,
            min_order_cases=command.min_order_cases,
            internal_contacts=self._clean_contacts(command.internal_contacts),
            ordering=self._clean_ordering(command.ordering),
            store_references=self._clean_store_references(
                command.store_references
            ),
            updated_at=self._now(),
        )

        self._vendors.save(updated)

        return updated

    def deactivate_vendor(self, vendor_id: str) -> Vendor:
        vendor = self.get_vendor(vendor_id)

        updated = replace(
            vendor,
            is_active=False,
            updated_at=self._now(),
        )

        self._vendors.save(updated)

        return updated

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

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

    @classmethod
    def _clean_contacts(
        cls,
        contacts: tuple[ContactInfo, ...],
    ) -> tuple[ContactInfo, ...]:
        return tuple(
            ContactInfo(
                name=cls._required_text(contact.name, "contact name"),
                title=cls._clean_text(contact.title),
                email=cls._clean_text(contact.email),
                phone=cls._clean_text(contact.phone),
            )
            for contact in contacts
        )

    @classmethod
    def _clean_ordering(cls, ordering: OrderingInfo) -> OrderingInfo:
        return OrderingInfo(
            method=tuple(
                cleaned
                for value in ordering.method
                if (cleaned := cls._clean_optional(value)) is not None
            ),
            email=cls._clean_text(ordering.email),
            portal_url=cls._clean_text(ordering.portal_url),
            phone_number=cls._clean_text(ordering.phone_number),
            schedule=tuple(
                ScheduleEntry(
                    order_day=cls._required_text(
                        entry.order_day,
                        "order day",
                    ),
                    delivery_days=tuple(
                        cleaned
                        for value in entry.delivery_days
                        if (cleaned := cls._clean_optional(value)) is not None
                    ),
                    cutoff_time=cls._clean_text(entry.cutoff_time),
                )
                for entry in ordering.schedule
            ),
        )

    @classmethod
    def _clean_schedule(
        cls,
        schedule: tuple[ScheduleEntry, ...],
    ) -> tuple[ScheduleEntry, ...]:
        cleaned_schedule: list[ScheduleEntry] = []

        for entry in schedule:
            order_day = cls._required_text(entry.order_day, "order day")

            cleaned_schedule.append(
                ScheduleEntry(
                    order_day=order_day,
                    delivery_days=tuple(
                        delivery_day
                        for raw_delivery_day in entry.delivery_days
                        if (delivery_day := raw_delivery_day.strip())
                    ),
                    cutoff_time=cls._clean_text(entry.cutoff_time),
                )
            )

        return tuple(cleaned_schedule)


    @classmethod
    def _clean_store_references(
        cls,
        store_references: tuple[VendorStoreReference, ...],
    ) -> tuple[VendorStoreReference, ...]:
        return tuple(
            VendorStoreReference(
                store_id=cls._required_text(reference.store_id, "store id"),
                vendor_store_reference=cls._clean_text(
                    reference.vendor_store_reference
                ),
            )
            for reference in store_references
        )