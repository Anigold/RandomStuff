from backend.app.ports.repos import VendorRepository
from backend.app.ports.files import VendorFilePort

from typing import Dict, Optional
from pathlib import Path

from backend.domain.models import Vendor
from backend.infra.paths import VENDOR_FILES_DIR

class VendorRegistry(VendorRepository):

    def __init__(self, files: VendorFilePort) -> None:
        self._files = files
        self._cache: Dict[str, Vendor] = {}

    def get_vendor(self, key: str) -> Optional[Vendor]:

        if not self._cache: self.list_all()

        target = key.strip().lower()

        for name, vendor in self._cache.items():
            if name.lower() == target:
                return vendor
            
        return None
    
    def list_all(self) -> List[Vendor]:

        if not self._cache:
            vendors = self._files.list_vendor_files()