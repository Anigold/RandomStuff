from __future__ import annotations
from dataclasses import dataclass

# from backend.app.ports.repos import VendorRepository
from backend.domain.models import Store
from backend.infra.logger import Logger

from backend.app.ports.repos import StoreRepository
# from backend.app.ports.files import StoreFilePort

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
        self.logger.info("Listing all stores.")
        return self.repo.list_all()


