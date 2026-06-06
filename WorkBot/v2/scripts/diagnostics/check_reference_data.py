from __future__ import annotations

from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository
)

from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository
)

from workbot_core.infrastructure.database.session import create_session


def main() -> None:
    with create_session() as session:
        stores = SqlStoreRepository(session)
        vendors = SqlVendorRepository(session)
        items = SqlItemRepository(session)
        users = SqlUserRepository(session)

        all_stores = stores.list_all()
        all_vendors = vendors.list_all()
        all_items = items.list_all()
        all_users = users.list_all()

    print("Stores:")
    print(f"  Count: {len(all_stores)}")
    for store in all_stores:
        print(f"  - {store.id}: {store.name} active={store.is_active}")

    print()
    print("Vendors:")
    print(f"  Count: {len(all_vendors)}")
    for vendor in all_vendors:
        print(f"  - {vendor.id}: {vendor.name} active={vendor.is_active}")

    # print()
    # print("Items:")
    # print(f"  Count: {len(all_items)}")
    # for item in all_items:
    #     print(f"  - {item.id}: {item.name} active={item.is_active}")

        print()
    print("Users:")
    print(f"  Count: {len(all_items)}")
    for user in all_users:
        print(user)


if __name__ == "__main__":
    main()