from backend.domain.models import Vendor
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

    def get_vendor(self, vendor: str) -> Vendor:
        file_path = self.get_file_path(vendor)
        return self.read_from_path(file_path)


    def list_vendors(self) -> List[Vendor]:
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
    
