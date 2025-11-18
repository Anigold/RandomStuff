from __future__ import annotations
from dataclasses import dataclass
from backend.app.ports import VendorRepository, DownloadPort



from dataclasses import dataclass

from backend.domain.models import Vendor
from backend.infra.logger import Logger

from backend.app.ports import VendorRepository
# ---- Queries ----

@Logger.attach_logger
@dataclass(frozen=True)
class GetVendor:
    
    repo: VendorRepository

    def __call__(self, name: str) -> Vendor:
        return self.repo.get(name)


@Logger.attach_logger
@dataclass(frozen=True)
class ListVendors:
    
    repo: VendorRepository

    def __call__(self) -> list[Vendor]:
        return self.repo.list_all()


# ---- Commands ----

# @Logger.attach_logger
# @dataclass(frozen=True)
# class SaveVendor:
#     repo: VendorRepository

#     def __call__(self, vendor: Vendor) -> None:
#         self.logger.info(f"Saving vendor: {vendor.name}")
#         self.repo.save_vendor(vendor)


# @Logger.attach_logger
# @dataclass(frozen=True)
# class RemoveVendor:
#     repo: VendorRepository

#     def __call__(self, name: str) -> None:
#         self.logger.info(f"Removing vendor: {name}")
#         self.repo.remove_vendor(name)


@dataclass
class VendorServices:

    repo:      VendorRepository
    downloads: DownloadPort

    def __post_init__(self):
        self.get_vendor   = GetVendor(self.repo)
        self.list_vendors = ListVendors(self.repo)

    # def get_vendor_info(self, name: str):
    #     return self.repo.get_vendor(name)

    # def list_all_vendors(self):
    #     return self.repo.list_vendors()