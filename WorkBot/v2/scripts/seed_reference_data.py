from __future__ import annotations

from decimal import Decimal

from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.utils.ids import IdGenerator


STORE_NAMES = [
    "Bakery",
    "Triphammer",
    "Collegetown",
    "Easthill",
    "Downtown",
]

VENDOR_NAMES = [
    "Russo Produce",
    "Hill & Markes",
]


def main() -> None:
    stores_created = 0
    vendors_created = 0

    with create_session() as session:
        stores = SqlStoreRepository(session)
        vendors = SqlVendorRepository(session)

        for store_name in STORE_NAMES:
            existing = stores.get_by_name(store_name)

            if existing is not None:
                continue

            store = Store(
                id=IdGenerator.store_id(exists=stores.exists),
                name=store_name,
            )

            stores.save(store)
            stores_created += 1

        for vendor_name in VENDOR_NAMES:
            existing = vendors.get_by_name(vendor_name)

            if existing is not None:
                continue

            vendor = Vendor(
                id=IdGenerator.vendor_id(exists=vendors.exists),
                name=vendor_name,
                min_order_value=Decimal("0"),
            )

            vendors.save(vendor)
            vendors_created += 1

        session.commit()

    print("Seeded reference data.")
    print(f"  Stores created:  {stores_created}")
    print(f"  Vendors created: {vendors_created}")


if __name__ == "__main__":
    main()