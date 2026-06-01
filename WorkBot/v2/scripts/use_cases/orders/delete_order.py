from __future__ import annotations

import argparse

from workbot_core.infrastructure.database.repositories.order_repository import (
    SqlOrderRepository,
)
from workbot_core.infrastructure.database.session import create_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete an order and its order lines.")

    parser.add_argument(
        "order_id",
        help="Order ID to delete, for example: ord_H4WMQMGP2J",
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm deletion without an interactive prompt.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        orders = SqlOrderRepository(session)
        order = orders.get_by_id(args.order_id)

        if order is None:
            print(f"Order not found: {args.order_id}")
            return

        print("Order found:")
        print(f"  ID:          {order.id}")
        print(f"  Store ID:    {order.store_id}")
        print(f"  Vendor ID:   {order.vendor_id}")
        print(f"  Order date:  {order.order_date}")
        print(f"  Status:      {order.status.value}")
        print(f"  Lines:       {len(order.lines)}")
        print(f"  Source:      {order.source}")
        print(f"  Reference:   {order.source_reference}")

        if not args.yes:
            response = input("\nDelete this order and all of its lines? Type DELETE to confirm: ")

            if response != "DELETE":
                print("Cancelled.")
                return

        orders.delete(order.id)
        session.commit()

    print(f"Deleted order: {args.order_id}")


if __name__ == "__main__":
    main()