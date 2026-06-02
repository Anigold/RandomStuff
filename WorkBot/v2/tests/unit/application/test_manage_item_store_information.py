from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from tests.fakes.repositories import (
    FakeItemRepository,
    FakeItemStoreInfoRepository,
    FakeStoreRepository,
)
from workbot_core.application.dto.item_catalog_commands import (
    AddItemStoreInfoCommand,
    UpdateItemStoreInfoCommand,
)
from workbot_core.application.use_cases.manage_item_store_information import (
    ManageItemStoreInformation,
)
from workbot_core.domain.models.item import Item
from workbot_core.domain.models.item_store_info import ItemStoreInfo
from workbot_core.domain.models.store import Store


def test_update_store_info_saves_updated_info() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_existing",
        store_id="sto_existing",
        count_unit="old unit",
        par=Decimal("1"),
    )

    infos = FakeItemStoreInfoRepository([info])
    use_case = ManageItemStoreInformation(item_store_infos=infos)

    updated = use_case.update_store_info(
        UpdateItemStoreInfoCommand(
            item_id="itm_existing",
            info_id="isi_existing",
            count_unit="bag",
            par=Decimal("6"),
            is_active=True,
        )
    )

    saved = infos.get_by_id("isi_existing")

    assert saved == updated
    assert updated.id == "isi_existing"
    assert updated.item_id == "itm_existing"
    assert updated.store_id == "sto_existing"
    assert updated.count_unit == "bag"
    assert updated.par == Decimal("6")
    assert updated.is_active is True


def test_update_store_info_cleans_optional_text_fields() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_existing",
        store_id="sto_existing",
    )

    infos = FakeItemStoreInfoRepository([info])
    use_case = ManageItemStoreInformation(item_store_infos=infos)

    updated = use_case.update_store_info(
        UpdateItemStoreInfoCommand(
            item_id="itm_existing",
            info_id="isi_existing",
            count_unit="  bag  ",
            is_active=True,
        )
    )

    assert updated.count_unit == "bag"


def test_update_store_info_converts_blank_optional_text_to_none() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_existing",
        store_id="sto_existing",
        count_unit="bag",
    )

    infos = FakeItemStoreInfoRepository([info])
    use_case = ManageItemStoreInformation(item_store_infos=infos)

    updated = use_case.update_store_info(
        UpdateItemStoreInfoCommand(
            item_id="itm_existing",
            info_id="isi_existing",
            count_unit="   ",
            is_active=True,
        )
    )

    assert updated.count_unit is None


def test_update_store_info_rejects_missing_info() -> None:
    use_case = ManageItemStoreInformation(
        item_store_infos=FakeItemStoreInfoRepository(),
    )

    with pytest.raises(
        ValueError,
        match="Item store info not found: isi_missing",
    ):
        use_case.update_store_info(
            UpdateItemStoreInfoCommand(
                item_id="itm_existing",
                info_id="isi_missing",
            )
        )


def test_update_store_info_rejects_info_for_different_item() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_other",
        store_id="sto_existing",
    )

    use_case = ManageItemStoreInformation(
        item_store_infos=FakeItemStoreInfoRepository([info]),
    )

    with pytest.raises(
        ValueError,
        match="Item store info not found: isi_existing",
    ):
        use_case.update_store_info(
            UpdateItemStoreInfoCommand(
                item_id="itm_existing",
                info_id="isi_existing",
            )
        )


def test_deactivate_store_info_sets_is_active_false() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_existing",
        store_id="sto_existing",
        is_active=True,
    )

    infos = FakeItemStoreInfoRepository([info])
    use_case = ManageItemStoreInformation(item_store_infos=infos)

    deactivated = use_case.deactivate_store_info(
        item_id="itm_existing",
        info_id="isi_existing",
    )

    saved = infos.get_by_id("isi_existing")

    assert saved == deactivated
    assert deactivated.id == "isi_existing"
    assert deactivated.item_id == "itm_existing"
    assert deactivated.store_id == "sto_existing"
    assert deactivated.is_active is False


def test_deactivate_store_info_rejects_missing_info() -> None:
    use_case = ManageItemStoreInformation(
        item_store_infos=FakeItemStoreInfoRepository(),
    )

    with pytest.raises(
        ValueError,
        match="Item store info not found: isi_missing",
    ):
        use_case.deactivate_store_info(
            item_id="itm_existing",
            info_id="isi_missing",
        )


def test_deactivate_store_info_rejects_info_for_different_item() -> None:
    info = _item_store_info(
        id="isi_existing",
        item_id="itm_other",
        store_id="sto_existing",
    )

    use_case = ManageItemStoreInformation(
        item_store_infos=FakeItemStoreInfoRepository([info]),
    )

    with pytest.raises(
        ValueError,
        match="Item store info not found: isi_existing",
    ):
        use_case.deactivate_store_info(
            item_id="itm_existing",
            info_id="isi_existing",
        )


def _item_store_info(
    *,
    id: str,
    item_id: str,
    store_id: str,
    count_unit: str | None = None,
    par: Decimal | None = None,
    is_active: bool = True,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ItemStoreInfo:
    return ItemStoreInfo(
        id=id,
        item_id=item_id,
        store_id=store_id,
        count_unit=count_unit,
        par=par,
        is_active=is_active,
        created_at=created_at,
        updated_at=updated_at,
    )