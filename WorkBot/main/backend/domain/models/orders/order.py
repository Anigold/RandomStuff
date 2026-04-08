from .order_item import OrderItem
from dataclasses import dataclass, field

@dataclass
class Order:

    store: str
    vendor: str
    date: str
    items: list[OrderItem]
    total_cost: float = field(init=False)

    def __post_init__(self):
        self.total_cost = sum([item.total_cost for item in self.items])
    