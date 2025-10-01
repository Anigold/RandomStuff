from backend.app.ports.repos import StoreRepository
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore
from pathlib import Path
from backend.domain.models import Store
from backend.domain.serializer.serializers.store import StoreSerializer
from backend.domain.naming.store_namer import StoreFilenameStrategy
from typing import List

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
        return []
    
    def save(self, store: Store) -> None:
        return
    
    def remove(self, store_name: str) -> None:
        return 