# workbot_core/application/use_cases/manage_stores.py

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from workbot_core.application.dto.store_commands import (
    CreateStoreCommand,
    UpdateStoreCommand,
)
from workbot_core.application.interfaces.repositories import StoreRepository
from workbot_core.domain.models.store import Store
from workbot_core.utils.ids import IdGenerator


class ManageStores:
    def __init__(
        self,
        *,
        stores: StoreRepository,
    ) -> None:
        self._stores = stores

    def create_store(self, command: CreateStoreCommand) -> Store:
        existing = self._stores.get_by_name(command.name)

        if existing is not None:
            raise ValueError(f"Store already exists: {command.name}")

        now = self._now()

        store = Store(
            id=IdGenerator.store_id(),
            name=self._required_text(command.name, "store name"),
            is_active=command.is_active,
            general_manager=self._clean_optional(command.general_manager),
            inventory_clerk=self._clean_optional(command.inventory_clerk),
            address=self._clean_optional(command.address),
            phone_number=self._clean_optional(command.phone_number),
            special_notes=self._clean_text(command.special_notes),
            created_at=now,
            updated_at=now,
        )

        self._stores.save(store)

        return store

    def list_stores(
        self,
        *,
        include_inactive: bool = True,
        search: str | None = None,
    ) -> list[Store]:
        if include_inactive:
            stores = self._stores.list_all()
        else:
            stores = self._stores.list_active()

        if search:
            normalized = search.casefold().strip()
            stores = [
                store
                for store in stores
                if normalized in store.name.casefold()
            ]

        return stores

    def get_store(self, store_id: str) -> Store:
        store = self._stores.get_by_id(store_id)

        if store is None:
            raise ValueError(f"Store not found: {store_id}")

        return store

    def update_store(self, command: UpdateStoreCommand) -> Store:
        store = self._stores.get_by_id(command.store_id)

        if store is None:
            raise ValueError(f"Store not found: {command.store_id}")

        existing = self._stores.get_by_name(command.name)

        if existing is not None and existing.id != store.id:
            raise ValueError(f"Store already exists: {command.name}")

        updated = replace(
            store,
            name=self._required_text(command.name, "store name"),
            is_active=command.is_active,
            general_manager=self._clean_optional(command.general_manager),
            inventory_clerk=self._clean_optional(command.inventory_clerk),
            address=self._clean_optional(command.address),
            phone_number=self._clean_optional(command.phone_number),
            special_notes=self._clean_text(command.special_notes),
            updated_at=self._now(),
        )

        self._stores.save(updated)

        return updated

    def deactivate_store(self, store_id: str) -> Store:
        store = self._stores.get_by_id(store_id)

        if store is None:
            raise ValueError(f"Store not found: {store_id}")

        updated = replace(
            store,
            is_active=False,
            updated_at=self._now(),
        )

        self._stores.save(updated)

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