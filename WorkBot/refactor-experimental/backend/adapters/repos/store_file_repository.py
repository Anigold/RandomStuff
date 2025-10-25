from backend.app.ports.repos import StoreRepository
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore
from pathlib import Path
from backend.domain.models import Store
from backend.domain.serializer.serializers.store import StoreSerializer
from backend.domain.naming.store_namer import StoreFilenameStrategy
from typing import List
from backend.infra.logger import Logger

@Logger.attach_logger
class StoreFileRepository(StoreRepository):

    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Store](
            store=LocalBlobStore(),
            serializer=StoreSerializer(),
            namer=StoreFilenameStrategy(base=base_dir),
        )

    def get(self, store_name):
        return ''
    
    def list_all(self) -> List[Store]:
        
        paths = self._engine.list_files("*.json")
        stores = []
        for path in paths:
            try:
                store = self._engine.read_from_path(path)
                stores.append(store)
            except Exception as e:
                self.logger.warning(f"Skipping unreadable store file {path}: {e}")
        return stores
    
    def save(self, store: Store) -> None:
        return
    
    def remove(self, store_name: str) -> None:
        return 