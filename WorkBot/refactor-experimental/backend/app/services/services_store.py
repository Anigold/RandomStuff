from dataclasses import dataclass
from backend.app.ports import (StoreFilePort, OrderRepository, DownloadPort)

from backend.app.application.stores import (
    GetStore,
    ListStores
)
@dataclass
class StoreServices:

    files:     StoreFilePort
    repo:      OrderRepository # CHANGE THIS WHEN DB INTEGRATATION IN FINISHED
    downloads: DownloadPort

    def __post_init__(self):
        self.get_store = GetStore(self.files)
        self.list_stores = ListStores(self.files)

    # def get_vendor_info(self, name: str):
    #     return self.repo.get_vendor(name)

    # def list_all_vendors(self):
    #     return self.repo.list_vendors()