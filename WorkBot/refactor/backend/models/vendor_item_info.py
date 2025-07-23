from dataclasses import dataclass, asdict


@dataclass(eq=True, frozen=False)
class VendorItemInfo:
    """
    Represents a vendor-specific version of an item.
    """
    sku: str
    unit: str
    quantity: float
    cost: float
    case_size: str

    def to_dict(self) -> dict:
        return asdict(self)
