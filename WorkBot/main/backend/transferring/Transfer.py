from dataclasses import dataclass
from datetime import datetime

@dataclass(unsafe_hash=True, frozen=True)
class TransferItem:
    name:     str
    quantity: float

@dataclass(unsafe_hash=True, frozen=True)
class Transfer:
    store_from: str
    store_to:   str
    # items:      list[TransferItem]
    date:       datetime
