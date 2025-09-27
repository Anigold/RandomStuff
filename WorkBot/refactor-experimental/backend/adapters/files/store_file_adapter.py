from backend.domain.models import Store
from backend.app.ports.files import StoreFilePort
from pathlib import Path
from backend.adapters.files.local_blob_store import LocalBlobStore
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.store import StoreSerializer
from backend.domain.naming.store_namer import StoreFilenameStrategy
from backend.infra.logger import Logger

from typing import List

@Logger.attach_logger
class StoreFileAdapter(StoreFilePort):
    
    def __init__(self, base_dir: Path):

        self._engine = GenericFileAdapter[Store](
            store=LocalBlobStore(),
            serializer=StoreSerializer(),
            namer=StoreFilenameStrategy(base=base_dir),
        )

    def save(self, store: Store, format: str = 'json') -> Path:
        return self._engine.save(store, format)

    def read_from_path(self, path: Path) -> Store:
        return self._engine.read(path)

    def get_file_path(self, store: Store, format: str = "json") -> Path:
        return self._engine.path_for(store, format)

    def remove(self, path: Path) -> None:
        self._engine.remove(path)

    def move(self, src: Path, dest: Path, overwrite: bool = False) -> None:
        self._engine.move(src, dest, overwrite=overwrite)

    def get_directory(self) -> Path:
        return self._engine.get_directory()

    def get_store(self, store: str) -> Store:
        file_path = self.get_file_path(store)
        return self.read_from_path(file_path)


    def list_stores(self) -> List[Store]:
        stores: List[Store] = []

        for ext in ('*.json', '*.yaml', '*.yml'):
            for path in self._engine.list_paths(ext):
                
                try:
                    store = self._engine.read(path)
                    stores.append(store)
                except Exception as e:
                    self.logger.warning(f'Skipped {path}: {e}')
                    # Empty vendor files break CLI autocompete?!
                    continue

        return stores
    
