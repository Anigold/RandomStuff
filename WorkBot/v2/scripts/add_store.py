from __future__ import annotations

import argparse

from workbot_core.domain.models.store import Store
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.utils.ids import IdGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a new store.")

    parser.add_argument("name")

    parser.add_argument("--general-manager")
    parser.add_argument("--inventory-clerk")
    parser.add_argument("--address")
    parser.add_argument("--phone-number")
    parser.add_argument("--special-notes", default="")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        stores = SqlStoreRepository(session)

        existing = stores.get_by_name(args.name)
        if existing is not None:
            print(f"Store already exists: {existing.id} / {existing.name}")
            return

        store = Store(
            id=IdGenerator.store_id(exists=stores.exists),
            name=args.name,
            general_manager=args.general_manager,
            inventory_clerk=args.inventory_clerk,
            address=args.address,
            phone_number=args.phone_number,
            special_notes=args.special_notes,
        )

        stores.save(store)
        session.commit()

    print("Store created.")
    print(f"  ID:   {store.id}")
    print(f"  Name: {store.name}")


if __name__ == "__main__":
    main()