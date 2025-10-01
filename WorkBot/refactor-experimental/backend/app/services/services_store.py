from dataclasses import dataclass
from backend.app.ports import DownloadPort
from backend.app.ports.repos import StoreRepository

from backend.app.application.stores import (
    GetStore,
    ListStores
)
@dataclass
class StoreServices:

    repo:      StoreRepository
    downloads: DownloadPort

    def __post_init__(self):
    
        self.get_store = GetStore(self.repo)
        self.list_stores = ListStores(self.repo)

    # def get_vendor_info(self, name: str):
    #     return self.repo.get_vendor(name)

    # def list_all_vendors(self):
    #     return self.repo.list_vendors()