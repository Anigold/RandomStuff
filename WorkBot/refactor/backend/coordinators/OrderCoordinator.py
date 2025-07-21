from storage.file.OrderFileHandler import OrderFileHandler
from storage.database.OrderDatabaseHandler import OrderDatabaseHandler
from parsers.OrderParser import OrderParser
from models.Order import Order

class OrderCoordinator:
    def __init__(self):
        self.file_handler = OrderFileHandler()
        self.db_handler   = OrderDatabaseHandler()
        self.parser       = OrderParser()

    # def import_order(self, order: Order, save_excel=True, persist_db=True) -> None:
    #     if save_excel:
    #         self.file_handler.save_order(order)
    #     if persist_db:
    #         self.db_handler.upsert_order(order)


    def save_order_file(self, order: Order):
        self.file_handler.save_order(order)

    def get_orders_from_file(self, store_names=None, vendor_names=None):
        return self.file_handler.get_orders(store_names, vendor_names)

    def get_orders_from_db(self, store, vendor):
        return self.db_handler.get_orders(store, vendor)
