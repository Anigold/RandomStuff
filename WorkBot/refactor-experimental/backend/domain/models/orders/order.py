from .order_item import OrderItem

class Order:

    def __init__(self, store: str, vendor: str, date: str, items: list[OrderItem] = None) -> None:
        self.store  = store
        self.vendor = vendor
        self.date   = date
        self.items  = items or []

    def __repr__(self) -> str:
        return f'< Order store={self.store}, vendor={self.vendor}, data={self.date}, items={len(self.items)} >'