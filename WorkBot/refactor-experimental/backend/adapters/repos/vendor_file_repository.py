from backend.app.ports.repos import VendorRepository

from typing import List
from pathlib import Path

from backend.domain.models import Vendor
from backend.infra.paths import VENDOR_FILES_DIR

from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore

from backend.domain.models import Vendor
from backend.domain.naming.vendor_namer import VendorFilenameStrategy
from backend.domain.serializer.serializers.vendor import VendorSerializer

class VendorFileRepository(VendorRepository):

    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Vendor](
            store=LocalBlobStore(),
            serializer=VendorSerializer(),
            namer=VendorFilenameStrategy(base=base_dir),
        )

    def get(self, vendor_name: str) -> Vendor:
        return ''
    
    def list_all(self) -> List[Vendor]:
        return []
    
    def save(self, vendor: Vendor) -> None:
        return
    
    def remove(self, vendor_name: str) -> None:
        return 