from dataclasses import dataclass, asdict


@dataclass(eq=True, frozen=False)
class VendorItemInfo:
    '''
    Represents a vendor-specific version of an item.
    '''
    vendor:   str
    sku:      str
    unit:     str
    quantity: float
    cost:     float

    def to_dict(self) -> dict:
        return asdict(self)
