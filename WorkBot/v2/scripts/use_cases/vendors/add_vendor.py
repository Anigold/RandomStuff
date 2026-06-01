from __future__ import annotations

import argparse
from decimal import Decimal

from workbot_core.domain.models.vendor import OrderingInfo, Vendor
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.utils.ids import IdGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a new vendor.")

    parser.add_argument("name")

    parser.add_argument("--order-format", default="")
    parser.add_argument("--special-notes", default="")
    parser.add_argument("--min-order-value", default="0")
    parser.add_argument("--min-order-cases", type=int, default=0)

    parser.add_argument("--ordering-email", default="")
    parser.add_argument("--portal-url", default="")
    parser.add_argument("--phone-number", default="")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        vendors = SqlVendorRepository(session)

        existing = vendors.get_by_name(args.name)
        if existing is not None:
            print(f"Vendor already exists: {existing.id} / {existing.name}")
            return

        vendor = Vendor(
            id=IdGenerator.vendor_id(exists=vendors.exists),
            name=args.name,
            order_format=args.order_format,
            special_notes=args.special_notes,
            min_order_value=Decimal(args.min_order_value),
            min_order_cases=args.min_order_cases,
            ordering=OrderingInfo(
                email=args.ordering_email,
                portal_url=args.portal_url,
                phone_number=args.phone_number,
            ),
        )

        vendors.save(vendor)
        session.commit()

    print("Vendor created.")
    print(f"  ID:   {vendor.id}")
    print(f"  Name: {vendor.name}")


if __name__ == "__main__":
    main()