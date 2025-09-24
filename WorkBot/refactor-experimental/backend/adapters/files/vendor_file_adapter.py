from backend.domain.models.vendor import Vendor
from backend.app.ports.files import VendorFilePort
from pathlib import Path
from backend.adapters.files.local_blob_store import LocalBlobStore
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.vendor import VendorSerializer
from backend.domain.naming.vendor_namer import VendorFilenameStrategy
from backend.infra.logger import Logger

from typing import List

@Logger.attach_logger
class VendorFileAdapter(VendorFilePort):
    
    def __init__(self, base_dir: Path):

        self._engine = GenericFileAdapter[Vendor](
            store=LocalBlobStore(),
            serializer=VendorSerializer(),
            namer=VendorFilenameStrategy(base=base_dir),
        )

    def save(self, vendor: Vendor, format: str = 'json') -> Path:
        return self._engine.save(vendor, format)

    def read_from_path(self, path: Path) -> Vendor:
        return self._engine.read(path)

    def get_file_path(self, vendor: Vendor, format: str = "json") -> Path:
        return self._engine.path_for(vendor, format)

    def remove(self, path: Path) -> None:
        self._engine.remove(path)

    def move(self, src: Path, dest: Path, overwrite: bool = False) -> None:
        self._engine.move(src, dest, overwrite=overwrite)

    def get_directory(self) -> Path:
        return self._engine.get_directory()


    def get_vendor(self, vendor: str) -> Vendor:
        file_path = self.get_file_path(vendor)
        return self.read_from_path(file_path)


    def list_vendor_files(self) -> List[Vendor]:
        vendors: List[Vendor] = []

        for ext in ('*.json', '*.yaml', '*.yml'):
            for path in self._engine.list_paths(ext):
                
                try:
                    vendor = self._engine.read(path)
                    vendors.append(vendor)
                except Exception as e:
                    self.logger.warning(f'Skipped {path}: {e}')
                    # Empty vendor files break CLI autocompete?!
                    continue

        return vendors
    
