from __future__ import annotations

from collections import Counter, defaultdict

from sqlalchemy import select

from workbot_core.infrastructure.database.records.item_record import ItemRecord
from workbot_core.infrastructure.database.records.item_store_info_record import (
    ItemStoreInfoRecord,
)
from workbot_core.infrastructure.database.records.item_vendor_info_record import (
    ItemVendorInfoRecord,
)
from workbot_core.infrastructure.database.records.store_record import StoreRecord
from workbot_core.infrastructure.database.records.vendor_record import VendorRecord
from workbot_core.infrastructure.database.session import create_session


def main() -> None:
    with create_session() as session:
        items = list(session.scalars(select(ItemRecord)).all())
        vendor_infos = list(session.scalars(select(ItemVendorInfoRecord)).all())
        store_infos = list(session.scalars(select(ItemStoreInfoRecord)).all())
        vendors = list(session.scalars(select(VendorRecord)).all())
        stores = list(session.scalars(select(StoreRecord)).all())

    item_ids = {item.id for item in items}
    vendor_ids = {vendor.id for vendor in vendors}
    store_ids = {store.id for store in stores}

    vendor_info_by_item_id = defaultdict(list)
    for info in vendor_infos:
        vendor_info_by_item_id[info.item_id].append(info)

    store_info_by_item_id = defaultdict(list)
    for info in store_infos:
        store_info_by_item_id[info.item_id].append(info)

    print("Imported item validation")
    print("========================")
    print()
    print("Counts")
    print(f"  Items:            {len(items)}")
    print(f"  Active items:     {sum(1 for item in items if item.is_active)}")
    print(f"  Inactive items:   {sum(1 for item in items if not item.is_active)}")
    print(f"  Vendors:          {len(vendors)}")
    print(f"  Stores:           {len(stores)}")
    print(f"  Vendor info rows: {len(vendor_infos)}")
    print(f"  Store info rows:  {len(store_infos)}")

    print()
    print("Potential issues")

    issues_found = False

    duplicate_names = _duplicate_item_names(items)
    if duplicate_names:
        issues_found = True
        print()
        print(f"  Duplicate item names: {len(duplicate_names)}")
        for name, count in duplicate_names[:20]:
            print(f"    - {name!r}: {count}")

    items_without_vendor_info = [
        item for item in items
        if item.is_active and item.id not in vendor_info_by_item_id
    ]
    if items_without_vendor_info:
        issues_found = True
        print()
        print(f"  Active items without vendor info: {len(items_without_vendor_info)}")
        for item in items_without_vendor_info[:20]:
            print(f"    - {item.id}: {item.name}")

    items_without_store_info = [
        item for item in items
        if item.is_active and item.id not in store_info_by_item_id
    ]
    if items_without_store_info:
        issues_found = True
        print()
        print(f"  Active items without store info: {len(items_without_store_info)}")
        for item in items_without_store_info[:20]:
            print(f"    - {item.id}: {item.name}")

    vendor_infos_without_sku = [
        info for info in vendor_infos
        if info.is_active and _is_blank(info.vendor_sku)
    ]
    if vendor_infos_without_sku:
        issues_found = True
        print()
        print(f"  Active vendor info rows without SKU: {len(vendor_infos_without_sku)}")
        for info in vendor_infos_without_sku[:20]:
            item_name = _item_name(item_ids=items, item_id=info.item_id)
            print(
                f"    - {info.id}: item_id={info.item_id}, "
                f"vendor_id={info.vendor_id}, item={item_name}"
            )

    vendor_infos_with_missing_item = [
        info for info in vendor_infos
        if info.item_id not in item_ids
    ]
    if vendor_infos_with_missing_item:
        issues_found = True
        print()
        print(
            "  Vendor info rows referencing missing items: "
            f"{len(vendor_infos_with_missing_item)}"
        )
        for info in vendor_infos_with_missing_item[:20]:
            print(f"    - {info.id}: item_id={info.item_id}")

    vendor_infos_with_missing_vendor = [
        info for info in vendor_infos
        if info.vendor_id not in vendor_ids
    ]
    if vendor_infos_with_missing_vendor:
        issues_found = True
        print()
        print(
            "  Vendor info rows referencing missing vendors: "
            f"{len(vendor_infos_with_missing_vendor)}"
        )
        for info in vendor_infos_with_missing_vendor[:20]:
            print(f"    - {info.id}: vendor_id={info.vendor_id}")

    store_infos_with_missing_item = [
        info for info in store_infos
        if info.item_id not in item_ids
    ]
    if store_infos_with_missing_item:
        issues_found = True
        print()
        print(
            "  Store info rows referencing missing items: "
            f"{len(store_infos_with_missing_item)}"
        )
        for info in store_infos_with_missing_item[:20]:
            print(f"    - {info.id}: item_id={info.item_id}")

    store_infos_with_missing_store = [
        info for info in store_infos
        if info.store_id not in store_ids
    ]
    if store_infos_with_missing_store:
        issues_found = True
        print()
        print(
            "  Store info rows referencing missing stores: "
            f"{len(store_infos_with_missing_store)}"
        )
        for info in store_infos_with_missing_store[:20]:
            print(f"    - {info.id}: store_id={info.store_id}")

    duplicate_vendor_info_keys = _duplicate_vendor_info_keys(vendor_infos)
    if duplicate_vendor_info_keys:
        issues_found = True
        print()
        print(f"  Duplicate item/vendor/SKU records: {len(duplicate_vendor_info_keys)}")
        for key, count in duplicate_vendor_info_keys[:20]:
            item_id, vendor_id, vendor_sku = key
            print(
                f"    - item_id={item_id}, vendor_id={vendor_id}, "
                f"vendor_sku={vendor_sku!r}: {count}"
            )

    duplicate_store_info_keys = _duplicate_store_info_keys(store_infos)
    if duplicate_store_info_keys:
        issues_found = True
        print()
        print(f"  Duplicate item/store records: {len(duplicate_store_info_keys)}")
        for key, count in duplicate_store_info_keys[:20]:
            item_id, store_id = key
            print(f"    - item_id={item_id}, store_id={store_id}: {count}")

    if not issues_found:
        print("  None found.")

    print()
    print("Validation complete.")


def _duplicate_item_names(items: list[ItemRecord]) -> list[tuple[str, int]]:
    counts = Counter(_normalize_name(item.name) for item in items)
    return sorted(
        ((name, count) for name, count in counts.items() if count > 1),
        key=lambda pair: pair[0],
    )


def _duplicate_vendor_info_keys(
    vendor_infos: list[ItemVendorInfoRecord],
) -> list[tuple[tuple[str, str, str | None], int]]:
    counts = Counter(
        (
            info.item_id,
            info.vendor_id,
            _normalize_optional(info.vendor_sku),
        )
        for info in vendor_infos
    )

    return sorted(
        ((key, count) for key, count in counts.items() if count > 1),
        key=lambda pair: pair[0],
    )


def _duplicate_store_info_keys(
    store_infos: list[ItemStoreInfoRecord],
) -> list[tuple[tuple[str, str], int]]:
    counts = Counter((info.item_id, info.store_id) for info in store_infos)

    return sorted(
        ((key, count) for key, count in counts.items() if count > 1),
        key=lambda pair: pair[0],
    )


def _normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    return cleaned or None


def _is_blank(value: str | None) -> bool:
    return _normalize_optional(value) is None


def _item_name(*, item_ids: set[str], item_id: str) -> str:
    # Placeholder fallback to avoid requiring a second lookup map in the print helper.
    # The caller already prints item_id, which is the important diagnostic key.
    if item_id in item_ids:
        return "<found>"

    return "<missing>"


if __name__ == "__main__":
    main()