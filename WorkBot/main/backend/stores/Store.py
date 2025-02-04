class Store():

    def __init__(self, name: str, store_id: str, craftable_id: str) -> None:
        self.name         = name
        self.id           = store_id
        self.craftable_id = craftable_id

stores = {}

Bakery      = Store('Bakery', '0')
Collegetown = Store('Collegetown', '1')
Downtown    = Store('Downtown', '2')
Easthill    = Store('Easthill', '3')
Triphammer  = Store('Triphammer', '4')

stores['Bakery']