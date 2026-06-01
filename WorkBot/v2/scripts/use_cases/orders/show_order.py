from __future__ import annotations

import argparse

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
    parser = argparse.ArgumentParser(description="Show full order details.")

    parser.add_argument(
        "order_id",
        help="Order ID to show, for example: ord_H4WMQMGP2J",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        orders = SqlOrderRepository(session)
        stores = SqlStoreRepository(session)
        vendors = SqlVendorRepository(session)

        order = orders.get_by_id(args.order_id)

        if order is None:
            print(f"Order not found: {args.order_id}")
            return

        store = stores.get_by_id(order.store_id)
        vendor = vendors.get_by_id(order.vendor_id)

    store_name = store.name if store else f"<missing store: {order.store_id}>"
    vendor_name = vendor.name if vendor else f"<missing vendor: {order.vendor_id}>"

    print("=" * 100)
    print("Order")
    print("=" * 100)
    print(f"ID:          {order.id}")
    print(f"Store:       {store_name} ({order.store_id})")
    print(f"Vendor:      {vendor_name} ({order.vendor_id})")
    print(f"Order date:  {order.order_date}")
    print(f"Delivery:    {order.delivery_date}")
    print(f"Status:      {order.status.value}")
    print(f"Source:      {order.source}")
    print(f"Reference:   {order.source_reference}")
    print(f"Lines:       {len(order.lines)}")

    if order.notes:
        print(f"Notes:       {order.notes}")

    print()
    print("=" * 100)
    print("Lines")
    print("=" * 100)

    if not order.lines:
        print("No lines found.")
        return

    for index, line in enumerate(order.lines, start=1):
        print("-" * 100)
        print(f"Line #{index}")
        print(f"  Line ID:              {line.id}")
        print(f"  Status:               {line.status.value}")
        print(f"  Source item name:     {line.source_item_name}")
        print(f"  Source vendor SKU:    {line.source_vendor_sku}")
        print(f"  Quantity:             {line.quantity}")
        print(f"  Unit:                 {line.unit}")
        print(f"  Unit price snapshot:  {line.unit_price_snapshot}")
        print(f"  Item ID:              {line.item_id}")
        print(f"  Item vendor info ID:  {line.item_vendor_info_id}")
        print(f"  Item name snapshot:   {line.item_name_snapshot}")
        print(f"  Vendor SKU snapshot:  {line.vendor_sku_snapshot}")
        print(f"  Moved to order ID:    {line.moved_to_order_id}")

        if line.status_reason:
            print(f"  Status reason:        {line.status_reason}")

        if line.notes:
            print(f"  Notes:                {line.notes}")


if __name__ == "__main__":
    main()