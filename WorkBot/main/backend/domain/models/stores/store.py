from dataclasses import dataclass, field


@dataclass
class StoreContact:

    name:  str
    title: str
    email: str
    phone: str


@dataclass
class Store:

    name: str
    code: str = ''                 # internal short code (e.g. BKY)
    special_notes: str = ''        # freeform notes
    address: str = ''              # street address
    phone_number: str = ''         # main store phone
    contacts: list[StoreContact] = field(default_factory=list)
