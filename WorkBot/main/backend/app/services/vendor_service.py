from __future__ import annotations

from dataclasses import dataclass

from backend.app.ports import VendorRepository, DownloadPort
from backend.domain.models import Vendor
from backend.domain.factories.vendor_factory import VendorFactory
from backend.infra.logger import Logger
# ---- Queries ----

@Logger.attach_logger
@dataclass(frozen=True)
class GetVendor:
    
    repo: VendorRepository

    def __call__(self, vendor_id: str) -> Vendor:
        return self.repo.get(vendor_id)
    

@Logger.attach_logger
@dataclass(frozen=True)
class GetVendorByName:
    repo: VendorRepository

    def __call__(self, name: str) -> Vendor | None:
        return self.repo.get_by_name(name)


@Logger.attach_logger
@dataclass(frozen=True)
class ListVendors:
    
    repo: VendorRepository

    def __call__(self) -> list[Vendor]:
        return self.repo.list_all()
    


    
@Logger.attach_logger
@dataclass(frozen=True)
class CreateVendor:
    repo: VendorRepository
    factory: VendorFactory

    def __call__(self, *, name: str, **kwargs) -> Vendor:
        vendor = self.factory.create(name=name, **kwargs)
        self.repo.save(vendor)
        return vendor
    


@Logger.attach_logger
@dataclass(frozen=True)
class RemoveVendor:
    repo: VendorRepository

    def __call__(self, vendor_id: str) -> None:
        self.repo.remove(vendor_id)


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

    repo: VendorRepository

    def __post_init__(self):

        factory = VendorFactory(self.repo)

        self.get_vendor = GetVendor(self.repo)
        self.get_vendor_by_name = GetVendorByName(self.repo)
        
        self.list_vendors = ListVendors(self.repo)
        
        self.create_vendor = CreateVendor(self.repo, factory)
        self.remove_vendor = RemoveVendor(self.repo)