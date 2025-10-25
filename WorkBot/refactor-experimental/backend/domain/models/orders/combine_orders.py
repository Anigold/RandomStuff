from dataclasses import dataclass
from typing import List, Any
from .order import Order
from collections import defaultdict
@dataclass(frozen=True)
class CombinedOrdersData:
    headers: List[str]
    rows: List[List[Any]]

class OrderCombiner:

    @staticmethod
    def combine(orders: List[Order]) -> CombinedOrdersData:

        if not orders:
            raise ValueError('No orders to merge.')
        
        item_map: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        store_names = sorted({o.store for o in orders})
        
        headers = ['Item Name'] + store_names

        for order in orders:
            for item in order.items:
                item_map[item.name][order.store] += float(item.quantity)

        rows = []
        for item_name, quantities in sorted(item_map.items()):
           row = [item_name] + [quantities.get(store, 0) for store in store_names]
           rows.append(row)

        return CombinedOrdersData(headers=headers, rows=rows)