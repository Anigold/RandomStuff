from __future__ import annotations

from decimal import Decimal

from workbot_core.domain.models.vendor import (
    ContactInfo,
    OrderingInfo,
    ScheduleEntry,
    Vendor,
    VendorStoreReference
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


def test_vendor_repository_saves_and_loads_vendor(db_session):
    vendors = SqlVendorRepository(db_session)

    vendor = Vendor(
        id="ven_TEST",
        name="Russo Produce",
        order_format="email",
        special_notes="Deliver to back door.",
        min_order_value=Decimal("150.00"),
        min_order_cases=3,
        internal_contacts=(
            ContactInfo(
                name="Jane Doe",
                title="Sales Rep",
                email="jane@example.com",
                phone="555-1111",
            ),
        ),
        ordering=OrderingInfo(
            method=("email",),
            email="orders@example.com",
            portal_url="",
            phone_number="555-2222",
            schedule=(
                ScheduleEntry(
                    order_day="Monday",
                    delivery_days=("Tuesday", "Wednesday"),
                    cutoff_time="12:00",
                ),
            ),
        ),
        store_references=(
            VendorStoreReference(
                store_id="str_TEST",
                vendor_store_reference="RUSSO-ITHACA",
            ),
        )
    )

    vendors.save(vendor)
    db_session.commit()

    saved = vendors.get_by_name("Russo Produce")

    assert saved is not None
    assert saved.id == "ven_TEST"
    assert saved.name == "Russo Produce"
    assert saved.order_format == "email"
    assert saved.special_notes == "Deliver to back door."
    assert saved.min_order_value == Decimal("150.00")
    assert saved.min_order_cases == 3
    assert saved.internal_contacts == vendor.internal_contacts
    assert saved.ordering == vendor.ordering
    assert saved.store_references == (
        VendorStoreReference(
            store_id="str_TEST",
            vendor_store_reference="RUSSO-ITHACA",
        ),
    )


def test_vendor_repository_lists_active_vendors(db_session):
    vendors = SqlVendorRepository(db_session)

    vendors.save(Vendor(id="ven_ACTIVE", name="Active Vendor", is_active=True))
    vendors.save(Vendor(id="ven_INACTIVE", name="Inactive Vendor", is_active=False))
    db_session.commit()

    active_vendors = vendors.list_active()

    assert len(active_vendors) == 1
    assert active_vendors[0].id == "ven_ACTIVE"