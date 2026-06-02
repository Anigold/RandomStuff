from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from workbot_core.application.dto.item_catalog_commands import (
    UpdateItemVendorInfoCommand,
)
from workbot_core.application.interfaces.repositories import ItemVendorInfoRepository
from workbot_core.application.use_cases.manage_item_vendor_information import (
    ManageItemVendorInformation,
)
from workbot_core.domain.models.item_vendor_info import ItemVendorInfo


class FakeItemVendorInfoRepository(ItemVendorInfoRepository):
    def __init__(
        self,
        infos: list[ItemVendorInfo] | None = None,
    ) -> None:
        self._infos: dict[str, ItemVendorInfo] = {}

        for info in infos or []:
            self._infos[info.id] = info

    def save(self, info: ItemVendorInfo) -> None:
        self._infos[info.id] = info

    def get_by_id(self, info_id: str) -> ItemVendorInfo | None:
        return self._infos.get(info_id)

    def list_for_item(self, item_id: str) -> list[ItemVendorInfo]:
        return [
            info
            for info in self._infos.values()
            if info.item_id == item_id
        ]

    def list_all(self) -> list[ItemVendorInfo]:
        return list(self._infos.values())

    def list_active(self) -> list[ItemVendorInfo]:
        return [
            info
            for info in self._infos.values()
            if info.is_active
        ]


def test_update_vendor_info_saves_updated_info() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_existing",
        vendor_id="ven_existing",
        vendor_sku="OLD-SKU",
        purchase_unit="old unit",
        pack_size=Decimal("1"),
        price=Decimal("10.00"),
    )

    infos = FakeItemVendorInfoRepository([info])
    use_case = ManageItemVendorInformation(item_vendor_infos=infos)

    updated = use_case.update_vendor_info(
        UpdateItemVendorInfoCommand(
            item_id="itm_existing",
            info_id="ivi_existing",
            vendor_sku="NEW-SKU",
            purchase_unit="case",
            pack_size=Decimal("12"),
            price=Decimal("42.50"),
            is_active=True,
        )
    )

    saved = infos.get_by_id("ivi_existing")

    assert saved == updated
    assert updated.id == "ivi_existing"
    assert updated.item_id == "itm_existing"
    assert updated.vendor_id == "ven_existing"
    assert updated.vendor_sku == "NEW-SKU"
    assert updated.purchase_unit == "case"
    assert updated.pack_size == Decimal("12")
    assert updated.price == Decimal("42.50")
    assert updated.is_active is True


def test_update_vendor_info_cleans_optional_text_fields() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_existing",
        vendor_id="ven_existing",
    )

    infos = FakeItemVendorInfoRepository([info])
    use_case = ManageItemVendorInformation(item_vendor_infos=infos)

    updated = use_case.update_vendor_info(
        UpdateItemVendorInfoCommand(
            item_id="itm_existing",
            info_id="ivi_existing",
            vendor_sku="  NEW-SKU  ",
            purchase_unit="  case  ",
            is_active=True,
        )
    )

    assert updated.vendor_sku == "NEW-SKU"
    assert updated.purchase_unit == "case"


def test_update_vendor_info_converts_blank_optional_text_to_none() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_existing",
        vendor_id="ven_existing",
        vendor_sku="OLD-SKU",
        purchase_unit="case",
    )

    infos = FakeItemVendorInfoRepository([info])
    use_case = ManageItemVendorInformation(item_vendor_infos=infos)

    updated = use_case.update_vendor_info(
        UpdateItemVendorInfoCommand(
            item_id="itm_existing",
            info_id="ivi_existing",
            vendor_sku="   ",
            purchase_unit="   ",
            is_active=True,
        )
    )

    assert updated.vendor_sku is None
    assert updated.purchase_unit is None


def test_update_vendor_info_rejects_missing_info() -> None:
    use_case = ManageItemVendorInformation(
        item_vendor_infos=FakeItemVendorInfoRepository(),
    )

    with pytest.raises(
        ValueError,
        match="Item vendor info not found: ivi_missing",
    ):
        use_case.update_vendor_info(
            UpdateItemVendorInfoCommand(
                item_id="itm_existing",
                info_id="ivi_missing",
            )
        )


def test_update_vendor_info_rejects_info_for_different_item() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_other",
        vendor_id="ven_existing",
    )

    use_case = ManageItemVendorInformation(
        item_vendor_infos=FakeItemVendorInfoRepository([info]),
    )

    with pytest.raises(
        ValueError,
        match="Item vendor info not found: ivi_existing",
    ):
        use_case.update_vendor_info(
            UpdateItemVendorInfoCommand(
                item_id="itm_existing",
                info_id="ivi_existing",
            )
        )


def test_deactivate_vendor_info_sets_is_active_false() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_existing",
        vendor_id="ven_existing",
        is_active=True,
    )

    infos = FakeItemVendorInfoRepository([info])
    use_case = ManageItemVendorInformation(item_vendor_infos=infos)

    deactivated = use_case.deactivate_vendor_info(
        item_id="itm_existing",
        info_id="ivi_existing",
    )

    saved = infos.get_by_id("ivi_existing")

    assert saved == deactivated
    assert deactivated.id == "ivi_existing"
    assert deactivated.item_id == "itm_existing"
    assert deactivated.vendor_id == "ven_existing"
    assert deactivated.is_active is False


def test_deactivate_vendor_info_rejects_missing_info() -> None:
    use_case = ManageItemVendorInformation(
        item_vendor_infos=FakeItemVendorInfoRepository(),
    )

    with pytest.raises(
        ValueError,
        match="Item vendor info not found: ivi_missing",
    ):
        use_case.deactivate_vendor_info(
            item_id="itm_existing",
            info_id="ivi_missing",
        )


def test_deactivate_vendor_info_rejects_info_for_different_item() -> None:
    info = _item_vendor_info(
        id="ivi_existing",
        item_id="itm_other",
        vendor_id="ven_existing",
    )

    use_case = ManageItemVendorInformation(
        item_vendor_infos=FakeItemVendorInfoRepository([info]),
    )

    with pytest.raises(
        ValueError,
        match="Item vendor info not found: ivi_existing",
    ):
        use_case.deactivate_vendor_info(
            item_id="itm_existing",
            info_id="ivi_existing",
        )


def _item_vendor_info(
    *,
    id: str,
    item_id: str,
    vendor_id: str,
    vendor_sku: str | None = None,
    purchase_unit: str | None = None,
    pack_size: Decimal | None = None,
    price: Decimal | None = None,
    last_purchase_date: datetime | None = None,
    is_active: bool = True,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ItemVendorInfo:
    return ItemVendorInfo(
        id=id,
        item_id=item_id,
        vendor_id=vendor_id,
        vendor_sku=vendor_sku,
        purchase_unit=purchase_unit,
        pack_size=pack_size,
        price=price,
        last_purchase_date=last_purchase_date,
        is_active=is_active,
        created_at=created_at,
        updated_at=updated_at,
    )