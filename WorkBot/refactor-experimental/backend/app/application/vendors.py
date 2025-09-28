from __future__ import annotations
from dataclasses import dataclass

# from backend.app.ports.repos import VendorRepository
from backend.domain.models import Vendor
from backend.infra.logger import Logger

# from backend.app.ports.files import VendorFilePort
from backend.app.ports import VendorRepository
# ---- Queries ----

@Logger.attach_logger
@dataclass(frozen=True)
class GetVendor:
    
    repo: VendorRepository

    def __call__(self, name: str) -> Vendor:
        self.logger.info(f"Fetching vendor: {name}")
        return self.files.get_vendor(name)


@Logger.attach_logger
@dataclass(frozen=True)
class ListVendors:
    
    files: VendorRepository

    def __call__(self) -> list[Vendor]:
        self.logger.info("Listing all vendors")
        return self.files.list_vendor_files()


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
