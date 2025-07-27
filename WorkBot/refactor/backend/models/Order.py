from .order_item import OrderItem
from dataclasses import dataclass, field
from typing import List

@dataclass
class Order:
    store:  str
    vendor: str
    date:   str
    items:  List[OrderItem] = field(default_factory=list)

    def __repr__(self) -> str:
        return f'< Order store={self.store}, vendor={self.vendor}, date={self.date}, items={len(self.items)} >'