from __future__ import annotations

from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.session import create_session


def main() -> None:
    with create_session() as session:
        vendors = SqlVendorRepository(session)
        all_vendors = vendors.list_all()

    print("Vendors:")
    for vendor in all_vendors:
        print(f"  - {vendor.name} ({vendor.id})")


if __name__ == "__main__":
    main()