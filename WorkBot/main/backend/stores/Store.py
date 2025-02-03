class Store():

    def __init__(self, name: str, vendors: list, id: str) -> None:
        self.name    = name
        self.vendors = vendors
        self.id      = id

stores = []

Bakery      = Store('Bakery', [], '0')
Collegetown = Store('Collegetown', [], '1')
Downtown    = Store('Downtown', [], '2')
Easthill    = Store('Easthill', [], '3')
Triphammer  = Store('Triphammer', [], '4')

stores.append(Bakery)
stores.append(Collegetown)
stores.append(Downtown)
stores.append(Easthill)
stores.append(Triphammer)