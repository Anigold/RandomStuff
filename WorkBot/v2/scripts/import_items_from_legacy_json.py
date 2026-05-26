from __future__ import annotations

import argparse
from pathlib import Path

from workbot_core.application.use_cases.import_items import ImportItems
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_store_info_repository import (
    SqlItemStoreInfoRepository,
)
from workbot_core.infrastructure.database.repositories.item_vendor_info_repository import (
    SqlItemVendorInfoRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.infrastructure.legacy.legacy_item_serializer import LegacyItemReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import legacy item JSON files into the WorkBot database."
    )

    parser.add_argument(
        "items_dir",
        type=Path,
        help="Directory containing legacy item JSON files.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run import and roll back instead of committing changes.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    reader = LegacyItemReader()
    rows = reader.read_directory(args.items_dir)

    print(f"Read {len(rows)} item file(s).")

    with create_session() as session:
        use_case = ImportItems(
            items=SqlItemRepository(session),
            item_vendor_infos=SqlItemVendorInfoRepository(session),
            item_store_infos=SqlItemStoreInfoRepository(session),
        )

        result = use_case.run(rows)

        if result.has_errors:
            session.rollback()
            action = "rolled back due to errors"
        elif args.dry_run:
            session.rollback()
            action = "rolled back dry run"
        else:
            session.commit()
            action = "committed"

    print()
    print("Item import complete.")
    print(f"  Action:  {action}")
    print(f"  Created: {result.created}")
    print(f"  Updated: {result.updated}")
    print(f"  Skipped: {result.skipped}")
    print(f"  Errors:  {len(result.errors)}")

    if result.errors:
        print()
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()