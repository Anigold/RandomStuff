from dataclasses import dataclass, field
from typing import List


@dataclass
class StoreContact:
    """Represents a person associated with a store (e.g. inventory clerk)."""
    name:  str
    title: str
    email: str
    phone: str


@dataclass
class Store:
    """Domain model for a Store location."""
    name: str
    code: str = ''                 # internal short code (e.g. BKY)
    special_notes: str = ''        # freeform notes
    address: str = ''              # street address
    phone_number: str = ''         # main store phone
    contacts: List[StoreContact] = field(default_factory=list)
