from pathlib import Path
from typing import Optional, List
from backend.domain.models import Item, VendorItemInfo, StoreItemInfo
from backend.core.interfaces.serializer import Serializer
from ..formats import get_formatter
from pprint import pprint
from collections import defaultdict

from backend.infra.logger import Logger
from backend.core.interfaces.formatter import BaseFormatter

@Logger.attach_logger
class ItemSerializer(Serializer[Item]):
    """
    Domain serializer: maps Order <-> dict.
    Delegates bytes conversion to a pluggable Formatter via the registry.
    """

    def __init__(self, default_format: str = 'json'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ---- Core protocol ----
    def dumps(self, obj: Item, format: Optional[str] = None, context: dict | None = None) -> bytes:

        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)

        item_dict = self.to_dict(obj)
        item_tabular = self._to_table(item_dict)
      

        return formatter.dumps(item_tabular, context=context)

    def loads(self, data: bytes, format: Optional[str] = None) -> Item:
        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload) 
        else:
            return self.from_dict(payload)

    def load_path(self, path: Path, context: dict | None = None) -> Item:

        fmt = path.suffix.lstrip(".").lower()
   
        formatter = self.get_formatter(fmt)

        payload = formatter.load_path(path, context=context)
    
        return self.from_table(payload)

    def get_formatter(self, fmt: str) -> BaseFormatter:
        return get_formatter(fmt)
    
    # ---- Domain <-> dict ----
    def to_dict(self, item: Item) -> dict:

        return {
            'name': item.name,
            'id': item.id,
            'vendor_info': [
                {
                    'vendor': v.vendor,
                    'sku': v.sku,
                    'unit': v.unit,
                    'quantity': v.quantity,
                    'cost': v.cost
                 }
                for v in item.vendor_info],
            'store_info': [
                {'quantity_on_hand': s.quantity_on_hand}
                for s in item.store_info],
        }


    def from_dict(self, data: dict) -> Item:
        return Item(
            name=data['name'],
            id=data['id'],
            vendor_info=[
                VendorItemInfo(
                    vendor=v['vendor'],
                    sku=v['sku'],
                    unit=v['unit'],
                    quantity=v['quantity'],
                    cost=v['cost']
                )
                for v in data['vendor_info']
            ],
            store_info=[
                StoreItemInfo(
                    quantity_on_hand=s['quantity_on_hand']
                )
                for s in data['store_info']
            ]
        )
        

    # def _to_table(self, order_dict: dict, context: dict | None = None) -> dict:
    #     metadata = {
    #         'store': order_dict.get('store', ''),
    #         'vendor': order_dict.get('vendor'),
    #         'date': order_dict.get('date', '')
    #     }

    #     headers = ['SKU', 'Name', 'Quantity', 'Cost Per', 'Total Cost']
    #     rows = [
    #         [i['sku'], i['name'], i['quantity'], i.get('cost_per', 0.0), i.get('total_cost', 0.0)]
    #         for i in order_dict.get('items', [])
    #     ]
    #     return {'metadata': metadata, 'headers': headers, 'rows': rows}
    
    # def from_table(self, table: dict) -> Order:

    #     headers = table.get("headers", [])
    #     rows = table.get("rows", [])
    #     meta = table.get("metadata", {})   # always pass it through

    #     items = []
    #     for row in rows:
    #         item_sku, item_name, qty, cost_per, total_cost = row
    #         item = {
    #             'sku': item_sku,
    #             'name': item_name,
    #             'quantity': qty,
    #             'cost_per': cost_per,
    #             'total_cost': total_cost,
    #         }
    #         items.append(item)

    #     data = {
    #         "metadata": meta,   # preserve metadata
    #         "items": items,
    #     }

    #     return self.from_dict(data)
    
    def _from_formatter(self, data: dict) -> Item:
        ...
        