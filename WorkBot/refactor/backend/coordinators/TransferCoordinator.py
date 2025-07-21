from models.Transfer import Transfer
class TransferCoordinator:
    def __init__(self, transfer_manager = None, order_manager = None):
        self.transfer_manager = transfer_manager
        self.order_manager = order_manager

    def create_transfer(self, item, quantity, source_location, destination_location):
        transfer = Transfer(item=item, quantity=quantity,
                            source_location=source_location,
                            destination_location=destination_location)
        self.transfer_manager.add_transfer(transfer)
        return transfer

    def process_transfer(self, transfer):
        if self.transfer_manager.validate_transfer(transfer):
            self.transfer_manager.execute_transfer(transfer)
            return True
        return False