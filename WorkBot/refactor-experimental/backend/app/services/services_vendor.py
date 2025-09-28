from dataclasses import dataclass
from backend.app.ports import (VendorFilePort, VendorRepository, DownloadPort)

from backend.app.application.vendors import (
    GetVendor,
    ListVendors
)
@dataclass
class VendorServices:

    # files:     VendorFilePort
    repo:      VendorRepository
    downloads: DownloadPort

    def __post_init__(self):
        self.get_vendor = GetVendor(self.repo)
        self.list_vendors = ListVendors(self.repo)

    # def get_vendor_info(self, name: str):
    #     return self.repo.get_vendor(name)

    # def list_all_vendors(self):
    #     return self.repo.list_vendors()