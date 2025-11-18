from __future__ import annotations
from dataclasses import dataclass
from backend.app.ports import DownloadPort
from backend.app.ports.repos import StoreRepository


from dataclasses import dataclass

from backend.domain.models import Store
from backend.infra.logger import Logger

from backend.app.ports.repos import StoreRepository

# ---- Queries ----

@Logger.attach_logger
@dataclass(frozen=True)
class GetStore:
    
    repo: StoreRepository

    def __call__(self, name: str) -> Store:
        self.logger.info(f"Fetching store: {name}")
        return self.repo.get(name)


@Logger.attach_logger
@dataclass(frozen=True)
class ListStores:
    
    repo: StoreRepository

    def __call__(self) -> list[Store]:
        return self.repo.list_all()



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