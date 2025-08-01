#asd
class Transfer:
    def __init__(self, item, quantity, source, destination):
        self.item = item
        self.quantity = quantity
        self.source = source
        self.destination = destination

    def execute(self):
        # Logic to execute the transfer
        pass

    def __repr__(self):
        return f"Transfer(item={self.item}, quantity={self.quantity}, source={self.source}, destination={self.destination})"