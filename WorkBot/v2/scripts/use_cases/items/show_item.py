from __future__ import annotations

import argparse

from sqlalchemy import select

from workbot_core.infrastructure.database.records.item_record import ItemRecord
from workbot_core.infrastructure.database.records.item_store_info_record import (
    ItemStoreInfoRecord,
)
from workbot_core.infrastructure.database.records.item_vendor_info_record import (
    ItemVendorInfoRecord,
)
from workbot_core.infrastructure.database.records.order_line_record import (
    OrderLineRecord,
)
from workbot_core.infrastructure.database.records.order_record import OrderRecord
from workbot_core.infrastructure.database.records.store_record import StoreRecord
from workbot_core.infrastructure.database.records.vendor_record import VendorRecord
from workbot_core.infrastructure.database.session import create_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show all known database information for an item."
    )

    parser.add_argument(
        "name",
        help="Exact item name to look up.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        item = session.scalars(
            select(ItemRecord).where(ItemRecord.name == args.name)
        ).one_or_none()

        if item is None:
            print(f"Item not found: {args.name}")
            return

        vendor_infos = list(
            session.scalars(
                select(ItemVendorInfoRecord).where(
                    ItemVendorInfoRecord.item_id == item.id
                )
            ).all()
        )

        store_infos = list(
            session.scalars(
                select(ItemStoreInfoRecord).where(
                    ItemStoreInfoRecord.item_id == item.id
                )
            ).all()
        )

        order_lines = list(
            session.scalars(
                select(OrderLineRecord).where(
                    OrderLineRecord.item_id == item.id
                )
            ).all()
        )

        source_name_order_lines = list(
            session.scalars(
                select(OrderLineRecord).where(
                    OrderLineRecord.source_item_name == item.name
                )
            ).all()
        )

        vendors_by_id = {
            vendor.id: vendor
            for vendor in session.scalars(select(VendorRecord)).all()
        }

        stores_by_id = {
            store.id: store
            for store in session.scalars(select(StoreRecord)).all()
        }

        orders_by_id = {
            order.id: order
            for order in session.scalars(select(OrderRecord)).all()
        }

    print("=" * 80)
    print("Item")
    print("=" * 80)
    print(f"ID:          {item.id}")
    print(f"Name:        {item.name}")
    print(f"Category:    {item.category}")
    print(f"Subcategory: {item.subcategory}")
    print(f"Count unit:  {item.count_unit}")
    print(f"Active:      {item.is_active}")
    print(f"Created:     {item.created_at}")
    print(f"Updated:     {item.updated_at}")

    print()
    print("=" * 80)
    print(f"Vendor Info ({len(vendor_infos)})")
    print("=" * 80)

    if not vendor_infos:
        print("No vendor info records found.")
    else:
        for info in vendor_infos:
            vendor = vendors_by_id.get(info.vendor_id)
            vendor_name = vendor.name if vendor else "<missing vendor>"

            print("-" * 80)
            print(f"ID:                 {info.id}")
            print(f"Vendor:             {vendor_name} ({info.vendor_id})")
            print(f"SKU:                {info.vendor_sku}")
            print(f"Purchase unit:      {info.purchase_unit}")
            print(f"Pack size:          {info.pack_size}")
            print(f"Price:              {info.price}")
            print(f"Last purchase date: {info.last_purchase_date}")
            print(f"Active:             {info.is_active}")

    print()
    print("=" * 80)
    print(f"Store Info ({len(store_infos)})")
    print("=" * 80)

    if not store_infos:
        print("No store info records found.")
    else:
        for info in store_infos:
            store = stores_by_id.get(info.store_id)
            store_name = store.name if store else "<missing store>"

            print("-" * 80)
            print(f"ID:         {info.id}")
            print(f"Store:      {store_name} ({info.store_id})")
            print(f"Count unit: {info.count_unit}")
            print(f"Par:        {info.par}")
            print(f"Active:     {info.is_active}")

    print()
    print("=" * 80)
    print(f"Resolved Order Lines ({len(order_lines)})")
    print("=" * 80)

    if not order_lines:
        print("No resolved order lines found for this item_id.")
    else:
        for line in order_lines:
            order = orders_by_id.get(line.order_id)

            print("-" * 80)
            print(f"Line ID:             {line.id}")
            print(f"Order ID:            {line.order_id}")
            print(f"Order date:          {order.order_date if order else '<missing order>'}")
            print(f"Status:              {line.status}")
            print(f"Source item name:    {line.source_item_name}")
            print(f"Source vendor SKU:   {line.source_vendor_sku}")
            print(f"Quantity:            {line.quantity}")
            print(f"Unit:                {line.unit}")
            print(f"Unit price snapshot: {line.unit_price_snapshot}")
            print(f"Vendor SKU snapshot: {line.vendor_sku_snapshot}")
            print(f"Status reason:       {line.status_reason}")

    print()
    print("=" * 80)
    print(f"Pending/Source-Matched Order Lines ({len(source_name_order_lines)})")
    print("=" * 80)

    if not source_name_order_lines:
        print("No order lines found with matching source_item_name.")
    else:
        for line in source_name_order_lines:
            order = orders_by_id.get(line.order_id)

            print("-" * 80)
            print(f"Line ID:             {line.id}")
            print(f"Order ID:            {line.order_id}")
            print(f"Order date:          {order.order_date if order else '<missing order>'}")
            print(f"Status:              {line.status}")
            print(f"Source item name:    {line.source_item_name}")
            print(f"Source vendor SKU:   {line.source_vendor_sku}")
            print(f"Quantity:            {line.quantity}")
            print(f"Unit price snapshot: {line.unit_price_snapshot}")
            print(f"Item ID:             {line.item_id}")
            print(f"Item vendor info ID: {line.item_vendor_info_id}")
            print(f"Status reason:       {line.status_reason}")


if __name__ == "__main__":
    main()