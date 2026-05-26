from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from workbot_core.domain.models.vendor import Vendor
from workbot_core.infrastructure.database.mappers.vendor_mapper import (
    update_vendor_record,
    vendor_record_to_domain,
    vendor_to_record,
)
from workbot_core.infrastructure.database.records.vendor_record import VendorRecord
from workbot_core.infrastructure.database.repositories.base_repository import SqlRepository


class SqlVendorRepository(SqlRepository[VendorRecord, Vendor]):
    def __init__(self, session: Session) -> None:
        super().__init__(
            session=session,
            record_type=VendorRecord,
            to_domain=vendor_record_to_domain,
            to_record=vendor_to_record,
            update_record=update_vendor_record,
        )

    def save(self, vendor: Vendor) -> None:
        super().save(vendor, vendor.id)

    def get_by_name(self, name: str) -> Vendor | None:
        statement = select(VendorRecord).where(VendorRecord.name == name)
        return self._one_or_none(statement)

    def list_active(self) -> list[Vendor]:
        statement = select(VendorRecord).where(VendorRecord.is_active.is_(True))
        return self._list(statement)