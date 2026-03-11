class OrderItem:

    def __init__(self, sku: str, name: str, quantity: float, cost_per: float, total_cost: float = None) -> None:
        self.sku        = sku
        self.name       = name
        self.quantity   = quantity
        self.cost_per   = cost_per
        self.total_cost = total_cost or (quantity * cost_per)