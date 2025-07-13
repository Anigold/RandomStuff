import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .VendorItemInfo import VendorItemInfo
from .StoreItemInfo import StoreItemInfo


@dataclass
class Item:
    """
    Represents a unique item in the system, potentially purchased from multiple vendors
    and stocked at multiple stores.
    """
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vendor_info: Dict[str, List[VendorItemInfo]] = field(default_factory=dict)
    store_info: Dict[str, StoreItemInfo] = field(default_factory=dict)

    def add_vendor_info(self, vendor: str, info: VendorItemInfo) -> None:
        if vendor not in self.vendor_info:
            self.vendor_info[vendor] = []

        if info not in self.vendor_info[vendor]:
            self.vendor_info[vendor].append(info)

    def add_store_info(self, store: str, info: StoreItemInfo) -> None:
        self.store_info[store] = info

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "vendors": {
                vendor: [vi.to_dict() for vi in infos]
                for vendor, infos in self.vendor_info.items()
            },
            "stores": {
                store: si.to_dict()
                for store, si in self.store_info.items()
            }
        }
