from backend.domain.models import Order, Transfer, TransferItem

def order_to_transfer(order: Order) -> Transfer:
    return Transfer(
        origin=order.vendor,
        destination_store=order.store,
        items=[
            TransferItem(
                sku=i.sku,
                name=i.name,
                quantity=i.quantity,
                cost=i.cost_per
            )
            for i in order.items
        ]
    )