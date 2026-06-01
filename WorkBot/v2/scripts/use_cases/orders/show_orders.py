from __future__ import annotations

import argparse
from datetime import date

from workbot_core.infrastructure.database.repositories.order_repository import (
    SqlOrderRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.session import create_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List imported orders.")

    parser.add_argument("--store")
    parser.add_argument("--vendor")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    start_date = date.fromisoformat(args.start_date) if args.start_date else None
    end_date = date.fromisoformat(args.end_date) if args.end_date else None

    with create_session() as session:
        orders = SqlOrderRepository(session)
        stores = SqlStoreRepository(session)
        vendors = SqlVendorRepository(session)

        stores_by_id = {store.id: store for store in stores.list_all()}
        vendors_by_id = {vendor.id: vendor for vendor in vendors.list_all()}

        store = stores.get_by_name(args.store) if args.store else None
        vendor = vendors.get_by_name(args.vendor) if args.vendor else None

        if args.store and store is None:
            raise RuntimeError(f"Store not found: {args.store}")

        if args.vendor and vendor is None:
            raise RuntimeError(f"Vendor not found: {args.vendor}")

        if store is not None and vendor is not None:
            order_list = orders.list_by_store_and_vendor(
                store.id,
                vendor.id,
                start_date=start_date,
                end_date=end_date,
            )
        elif store is not None:
            order_list = orders.list_by_store(
                store.id,
                start_date=start_date,
                end_date=end_date,
            )
        elif vendor is not None:
            order_list = orders.list_by_vendor(
                vendor.id,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            order_list = orders.list_all()

    if not order_list:
        print("No orders found.")
        return

    print("Orders")
    print("=" * 120)
    print(
        f"{'Order ID':<16} "
        f"{'Date':<12} "
        f"{'Store':<18} "
        f"{'Vendor':<24} "
        f"{'Status':<12} "
        f"{'Lines':>5} "
        f"{'Source':<12} "
        f"{'Reference'}"
    )
    print("-" * 120)

    for order in order_list:
        store_name = stores_by_id.get(order.store_id).name if order.store_id in stores_by_id else order.store_id
        vendor_name = vendors_by_id.get(order.vendor_id).name if order.vendor_id in vendors_by_id else order.vendor_id

        reference = order.source_reference or ""
        if len(reference) > 24:
            reference = reference[:21] + "..."

        print(
            f"{order.id:<16} "
            f"{str(order.order_date):<12} "
            f"{store_name:<18} "
            f"{vendor_name:<24} "
            f"{order.status.value:<12} "
            f"{len(order.lines):>5} "
            f"{(order.source or ''):<12} "
            f"{reference}"
        )

    print()
    print(f"Total orders: {len(order_list)}")


if __name__ == "__main__":
    main()