from .transfer_item import TransferItem

class Transfer:


    def __init__(self, transfer_items: list[(TransferItem, int)], origin: str, destination: str, transfer_date: str):

        self.transfer_items = transfer_items
        self.origin         = origin
        self.destination    = destination
        self.transfer_date  = transfer_date


    def __repr__(self) -> str:
        return f'< Transfer origin={self.origin}, destination={self.destination}, date={self.transfer_date}, items={len(self.transfer_items)} >'