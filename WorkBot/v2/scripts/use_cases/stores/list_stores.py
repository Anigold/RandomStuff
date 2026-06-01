from __future__ import annotations

from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.session import create_session


def main() -> None:
    with create_session() as session:
        stores = SqlStoreRepository(session)
        all_stores = stores.list_all()

    print("Stores:")
    for store in all_stores:
        print(f"  - {store.name} ({store.id})")


if __name__ == "__main__":
    main()