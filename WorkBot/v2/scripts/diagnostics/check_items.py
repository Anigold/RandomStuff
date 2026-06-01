from __future__ import annotations

from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.session import create_session


def main() -> None:
    with create_session() as session:
        items = SqlItemRepository(session)
        all_items = items.list_all()
        active_items = items.list_active()

    print("Items:")
    print(f"  Total:  {len(all_items)}")
    print(f"  Active: {len(active_items)}")

    print()
    print("First 20 items:")
    for item in all_items[:20]:
        print(f"  - {item.id}: {item.name}")


if __name__ == "__main__":
    main()