from __future__ import annotations

from decimal import Decimal

from workbot_core.application.dto.item_import_row import (
    ItemImportRow,
    ItemStoreInfoImportRow,
    ItemVendorInfoImportRow,
)
from workbot_core.application.use_cases.import_items import ImportItems
from workbot_core.domain.models.store import Store
from workbot_core.domain.models.vendor import Vendor
from workbot_core.infrastructure.database.repositories.item_repository import (
    SqlItemRepository,
)
from workbot_core.infrastructure.database.repositories.item_store_info_repository import (
    SqlItemStoreInfoRepository,
)
from workbot_core.infrastructure.database.repositories.item_vendor_info_repository import (
    SqlItemVendorInfoRepository,
)
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


def test_import_items_creates_item_with_vendor_and_store_info(db_session):
    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)

    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores.save(store)
    vendors.save(vendor)
    db_session.commit()

    row = ItemImportRow(
        id="itm_SMOKE_TEST",
        name="Smoke Test Item",
        category="Test",
        subcategory="Smoke",
        count_unit="each",
        is_active=True,
        vendor_info=(
            ItemVendorInfoImportRow(
                vendor_id=vendor.id,
                vendor_sku="SMOKE-001",
                purchase_unit="case",
                pack_size=Decimal("12"),
                price=Decimal("24.50"),
            ),
        ),
        store_info=(
            ItemStoreInfoImportRow(
                store_id=store.id,
                count_unit="each",
                par=Decimal("6"),
            ),
        ),
    )

    use_case = ImportItems(
        items=SqlItemRepository(db_session),
        item_vendor_infos=SqlItemVendorInfoRepository(db_session),
        item_store_infos=SqlItemStoreInfoRepository(db_session),
    )

    result = use_case.run([row])
    db_session.commit()

    assert not result.has_errors
    assert result.created == 1
    assert result.updated == 0

    items = SqlItemRepository(db_session)
    vendor_infos = SqlItemVendorInfoRepository(db_session)
    store_infos = SqlItemStoreInfoRepository(db_session)

    saved_item = items.get_by_id("itm_SMOKE_TEST")
    saved_vendor_info = vendor_infos.get_by_item_vendor_sku(
        item_id="itm_SMOKE_TEST",
        vendor_id=vendor.id,
        vendor_sku="SMOKE-001",
    )
    saved_store_info = store_infos.get_by_item_store(
        item_id="itm_SMOKE_TEST",
        store_id=store.id,
    )

    assert saved_item is not None
    assert saved_item.name == "Smoke Test Item"
    assert saved_item.category == "Test"
    assert saved_item.subcategory == "Smoke"
    assert saved_item.count_unit == "each"

    assert saved_vendor_info is not None
    assert saved_vendor_info.vendor_id == vendor.id
    assert saved_vendor_info.vendor_sku == "SMOKE-001"
    assert saved_vendor_info.purchase_unit == "case"
    assert saved_vendor_info.pack_size == Decimal("12.000")
    assert saved_vendor_info.price == Decimal("24.50")

    assert saved_store_info is not None
    assert saved_store_info.store_id == store.id
    assert saved_store_info.count_unit == "each"
    assert saved_store_info.par == Decimal("6.000")


def test_import_items_updates_existing_item(db_session):
    stores = SqlStoreRepository(db_session)
    vendors = SqlVendorRepository(db_session)

    store = Store(id="str_TEST", name="Bakery")
    vendor = Vendor(id="ven_TEST", name="Russo Produce")

    stores.save(store)
    vendors.save(vendor)
    db_session.commit()

    use_case = ImportItems(
        items=SqlItemRepository(db_session),
        item_vendor_infos=SqlItemVendorInfoRepository(db_session),
        item_store_infos=SqlItemStoreInfoRepository(db_session),
    )

    first_row = ItemImportRow(
        id="itm_SMOKE_TEST",
        name="Smoke Test Item",
        category="Test",
        subcategory="Smoke",
        count_unit="each",
        is_active=True,
        vendor_info=(
            ItemVendorInfoImportRow(
                vendor_id=vendor.id,
                vendor_sku="SMOKE-001",
                purchase_unit="case",
                pack_size=Decimal("12"),
                price=Decimal("24.50"),
            ),
        ),
        store_info=(
            ItemStoreInfoImportRow(
                store_id=store.id,
                count_unit="each",
                par=Decimal("6"),
            ),
        ),
    )

    second_row = ItemImportRow(
        id="itm_SMOKE_TEST",
        name="Updated Smoke Test Item",
        category="Updated",
        subcategory="Smoke",
        count_unit="case",
        is_active=True,
        vendor_info=(
            ItemVendorInfoImportRow(
                vendor_id=vendor.id,
                vendor_sku="SMOKE-001",
                purchase_unit="case",
                pack_size=Decimal("24"),
                price=Decimal("48.00"),
            ),
        ),
        store_info=(
            ItemStoreInfoImportRow(
                store_id=store.id,
                count_unit="case",
                par=Decimal("12"),
            ),
        ),
    )

    first_result = use_case.run([first_row])
    second_result = use_case.run([second_row])
    db_session.commit()

    assert not first_result.has_errors
    assert not second_result.has_errors
    assert first_result.created == 1
    assert second_result.updated == 1

    items = SqlItemRepository(db_session)
    vendor_infos = SqlItemVendorInfoRepository(db_session)
    store_infos = SqlItemStoreInfoRepository(db_session)

    saved_item = items.get_by_id("itm_SMOKE_TEST")
    saved_vendor_info = vendor_infos.get_by_item_vendor_sku(
        item_id="itm_SMOKE_TEST",
        vendor_id=vendor.id,
        vendor_sku="SMOKE-001",
    )
    saved_store_info = store_infos.get_by_item_store(
        item_id="itm_SMOKE_TEST",
        store_id=store.id,
    )

    assert saved_item is not None
    assert saved_item.name == "Updated Smoke Test Item"
    assert saved_item.category == "Updated"
    assert saved_item.count_unit == "case"

    assert saved_vendor_info is not None
    assert saved_vendor_info.pack_size == Decimal("24.000")
    assert saved_vendor_info.price == Decimal("48.00")

    assert saved_store_info is not None
    assert saved_store_info.count_unit == "case"
    assert saved_store_info.par == Decimal("12.000")