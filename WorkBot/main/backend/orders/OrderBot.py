from .Order import Order
from .OrderManager import OrderManager

class OrderBot:

    def __init__(self, order_manager: OrderManager) -> None:
        self.order_manager = order_manager

    def save_order(self, order: Order) -> None:
        