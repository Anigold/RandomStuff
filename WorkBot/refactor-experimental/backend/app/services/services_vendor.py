from dataclasses import dataclass
from backend.app.ports import (VendorFilePort, OrderRepository, DownloadPort)

from backend.app.application.vendors import (
    GetVendor,
    ListVendors
)
@dataclass
class VendorServices:

    files:     VendorFilePort
    repo:      OrderRepository # CHANGE THIS WHEN DB INTEGRATATION IN FINISHED
    downloads: DownloadPort

    def __post_init__(self):
        self.get_vendor = GetVendor(self.files)
        self.list_vendors = ListVendors(self.files)

    # def get_vendor_info(self, name: str):
    #     return self.repo.get_vendor(name)

    # def list_all_vendors(self):
    #     return self.repo.list_vendors()