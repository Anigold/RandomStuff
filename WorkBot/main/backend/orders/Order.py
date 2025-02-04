from ..stores.Store import Store

class Order:

    def __init__(self, store: Store, vendor: str, date: str, items: list = []) -> None:
        self.store = store
        self.vendor = vendor
        self.date = date
        self.items = items

    def load_items_from_file(path: str):
        pass