# scripts/migrate_vendor_ids.py

from __future__ import annotations

import json
from pathlib import Path

from backend.core.normalization.ids import IdGenerator
from backend.infra.paths import VENDOR_FILES_DIR


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def collect_existing_ids(vendor_files: list[Path]) -> set[str]:
    existing_ids: set[str] = set()

    for path in vendor_files:
        data = load_json(path)
        vendor_id = data.get("id")

        if vendor_id:
            if vendor_id in existing_ids:
                raise ValueError(
                    f"Duplicate vendor id '{vendor_id}' found before migration. "
                    f"Offending file: {path}"
                )
            existing_ids.add(vendor_id)

    return existing_ids


def generate_unique_vendor_id(existing_ids: set[str]) -> str:
    while True:
        candidate = IdGenerator.vendor_id()
        if candidate not in existing_ids:
            existing_ids.add(candidate)
            return candidate


def migrate_vendor_file(path: Path, existing_ids: set[str]) -> bool:
    data = load_json(path)

    current_id = data.get("id")
    if current_id:
        return False

    new_id = generate_unique_vendor_id(existing_ids)
    data["id"] = new_id
    save_json(path, data)

    print(f"[UPDATED] {path.name} -> id={new_id}")
    return True


def main() -> None:
    vendor_dir = Path(VENDOR_FILES_DIR)
    vendor_files = sorted(vendor_dir.glob("*.json"))

    if not vendor_files:
        print(f"No vendor JSON files found in: {vendor_dir}")
        return

    print(f"Found {len(vendor_files)} vendor file(s) in {vendor_dir}")

    existing_ids = collect_existing_ids(vendor_files)

    updated_count = 0
    skipped_count = 0

    for path in vendor_files:
        updated = migrate_vendor_file(path, existing_ids)
        if updated:
            updated_count += 1
        else:
            skipped_count += 1
            print(f"[SKIPPED] {path.name} already has an id")

    print("\nMigration complete.")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")


def run():
    main()