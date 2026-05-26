from __future__ import annotations

import argparse
from pathlib import Path

from workbot_core.application.use_cases.import_vendors import ImportVendors
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.infrastructure.legacy.legacy_vendor_serializer import LegacyVendorReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import legacy vendor JSON files into the WorkBot database."
    )

    parser.add_argument(
        "vendors_dir",
        type=Path,
        help="Directory containing legacy vendor JSON files.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run import and roll back instead of committing changes.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    reader = LegacyVendorReader()
    rows = reader.read_directory(args.vendors_dir)

    print(f"Read {len(rows)} vendor file(s).")

    with create_session() as session:
        use_case = ImportVendors(
            vendors=SqlVendorRepository(session),
            stores=SqlStoreRepository(session),
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
    print("Vendor import complete.")
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