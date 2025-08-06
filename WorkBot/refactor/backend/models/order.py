from .order_item import OrderItem

class Order:

    def __init__(self, store: str, vendor: str, date: str, items: list[OrderItem] = None) -> None:
        self.store  = store
        self.vendor = vendor
        self.date   = date
        self.items  = items or []