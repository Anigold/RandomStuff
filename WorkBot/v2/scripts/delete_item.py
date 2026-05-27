from __future__ import annotations

import argparse

from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.session import create_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete an item and its related item info records."
    )

    lookup = parser.add_mutually_exclusive_group(required=True)

    lookup.add_argument(
        "--item-id",
        help="Item ID to delete, for example: itm_ABC123",
    )

    lookup.add_argument(
        "--name",
        help='Exact item name to delete, for example: "Test Item - API Measurement"',
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
        items = SqlItemRepository(session)

        if args.item_id:
            item = items.get_by_id(args.item_id)
        else:
            item = items.get_by_name(args.name)

        if item is None:
            print("Item not found.")
            return

        print("Item found:")
        print(f"  ID:          {item.id}")
        print(f"  Name:        {item.name}")
        print(f"  Category:    {item.category}")
        print(f"  Subcategory: {item.subcategory}")
        print(f"  Count unit:  {item.count_unit_quantity} {item.count_unit_measure}")
        print(f"  Active:      {item.is_active}")

        print()
        print("WARNING:")
        print("  This may also remove related item vendor/store info if your database")
        print("  relationships are configured with cascade delete.")

        if not args.yes:
            response = input("\nDelete this item? Type DELETE to confirm: ")

            if response != "DELETE":
                print("Cancelled.")
                return

        items.delete(item.id)
        session.commit()

    print(f"Deleted item: {item.id} / {item.name}")


if __name__ == "__main__":
    main()