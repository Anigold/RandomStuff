from dataclasses import dataclass, asdict


@dataclass
class StoreItemInfo:
    """
    Represents store-specific inventory or tracking information for an item.
    """
    quantity_on_hand: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)
