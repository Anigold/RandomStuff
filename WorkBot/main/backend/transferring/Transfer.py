from dataclasses import dataclass

@dataclass(unsafe_hash=True, frozen=True)
class Transfer:
    store_from: str
    store_to: str
    items: list
    date: str