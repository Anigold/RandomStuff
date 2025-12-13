from .order_item import OrderItem

class Order:

    def __init__(self, store: str, vendor: str, date: str, items: list[OrderItem] = None) -> None:
        self.store  = store
        self.vendor = vendor
        self.date   = date
        self.items  = items or []
        self.total_cost = sum(item.total_cost for item in self.items)

    def __repr__(self) -> str:
        return f'< Order store={self.store}, vendor={self.vendor}, date={self.date}, items={len(self.items)} >'
    