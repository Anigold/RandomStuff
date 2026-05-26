from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from workbot_core.application.use_cases.import_order import ImportOrder
from workbot_core.application.use_cases.resolve_order_lines import ResolveOrderLines
from workbot_core.infrastructure.craftable.craftable_order_reader import (
    CraftableOrderReader,
    CraftableOrderReaderConfig,
)
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_vendor_info_repository import (
    SqlItemVendorInfoRepository,
)
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
    parser = argparse.ArgumentParser(
        description="Import a Craftable order Excel file into WorkBot."
    )

    parser.add_argument("path", type=Path)

    parser.add_argument(
        "--store",
        required=True,
        help='Store name, for example: "Bakery"',
    )

    parser.add_argument(
        "--vendor",
        required=True,
        help='Vendor name, for example: "Russo Produce"',
    )

    parser.add_argument(
        "--order-date",
        required=True,
        help="Order date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--delivery-date",
        help="Optional delivery date in YYYY-MM-DD format.",
    )

    parser.add_argument("--sheet-name")
    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument(
        "--resolve",
        action="store_true",
        help="Resolve pending order lines immediately after import.",
    )

    parser.add_argument("--sku-header", default="SKU")
    parser.add_argument("--item-header", default="Name")
    parser.add_argument("--quantity-header", default="Quantity")
    parser.add_argument("--unit-price-header", default="Cost per")
    parser.add_argument("--total-cost-header", default="Total Cost")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        stores = SqlStoreRepository(session)
        vendors = SqlVendorRepository(session)
        orders = SqlOrderRepository(session)

        store = stores.get_by_name(args.store)
        if store is None:
            raise RuntimeError(f"Store not found: {args.store}")

        vendor = vendors.get_by_name(args.vendor)
        if vendor is None:
            raise RuntimeError(f"Vendor not found: {args.vendor}")

        config = CraftableOrderReaderConfig(
            store_id=store.id,
            vendor_id=vendor.id,
            order_date=date.fromisoformat(args.order_date),
            delivery_date=(
                date.fromisoformat(args.delivery_date)
                if args.delivery_date
                else None
            ),
            source_reference=str(args.path),
            sheet_name=args.sheet_name,
            sku_header=args.sku_header,
            item_name_header=args.item_header,
            quantity_header=args.quantity_header,
            unit_price_header=args.unit_price_header,
            total_cost_header=args.total_cost_header,
        )

        reader = CraftableOrderReader()
        row = reader.read_file(args.path, config=config)

        import_result = ImportOrder(
            orders=orders,
            stores=stores,
            vendors=vendors,
        ).run(row)

        resolve_result = None

        if not import_result.has_errors and args.resolve and import_result.order_id:
            resolve_result = ResolveOrderLines(
                orders=orders,
                items=SqlItemRepository(session),
                item_vendor_infos=SqlItemVendorInfoRepository(session),
            ).run(import_result.order_id)

        if args.dry_run:
            session.rollback()
            action = "rolled back dry run"
        elif import_result.has_errors:
            session.rollback()
            action = "rolled back due to import errors"
        elif resolve_result is not None and resolve_result.has_errors:
            session.rollback()
            action = "rolled back due to resolution errors"
        else:
            session.commit()
            action = "committed"

    print()
    print("Craftable order import complete.")
    print(f"  Action:   {action}")
    print(f"  Store:    {args.store}")
    print(f"  Vendor:   {args.vendor}")
    print(f"  Imported: {import_result.created}")
    print(f"  Order ID: {import_result.order_id}")
    print(f"  Errors:   {len(import_result.errors)}")

    for error in import_result.errors:
        print(f"  - {error}")

    if resolve_result is not None:
        print()
        print("Resolution:")
        print(f"  Processed: {resolve_result.processed}")
        print(f"  Errored:   {resolve_result.errored}")
        print(f"  Skipped:   {resolve_result.skipped}")

        for error in resolve_result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()