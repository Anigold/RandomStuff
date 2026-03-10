from backend.app.ports.repos import VendorRepository

from typing import List
from pathlib import Path

from backend.domain.models import Vendor

from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.infra.filesystem.local_blob_store import LocalBlobStore

from backend.domain.models import Vendor
from backend.domain.naming.vendor_namer import VendorFilenameStrategy
from backend.domain.serializer.serializers.vendor import VendorSerializer

class VendorFileRepository(VendorRepository):

    # def __init__(self, base_dir: Path):
    #     self._engine = GenericFileAdapter[Vendor](
    #         store=LocalBlobStore(),
    #         serializer=VendorSerializer(),
    #         namer=VendorFilenameStrategy(base=base_dir),
    #     )

    # def get(self, name: str) -> Vendor:

    #     matches = self._engine.find(name=name)
    #     if not matches:
    #         raise FileNotFoundError(f"No vendor file found for {name}")
    #     return matches[0]

    # def list_all(self) -> List[Vendor]:
    #     return self._engine.find()

    # def save(self, vendor: Vendor) -> None:
    #     self._engine.save(vendor, format=self._engine.preferred_format())

    # def remove(self, name: str) -> None:
    #     try:
    #         vendor = Vendor(name=name)
    #         path = self._engine.get_file_path(vendor, format=self._engine.preferred_format())
    #         self._engine.remove(path)
    #     except FileNotFoundError:
    #         pass
    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Vendor](
            store=LocalBlobStore(),
            serializer=VendorSerializer(),
            namer=VendorFilenameStrategy(base=base_dir),
        )

    def get(self, vendor_id: str) -> Vendor:
        for vendor in self.list_all():
            if vendor.id == vendor_id:
                return vendor
        raise FileNotFoundError(f"No vendor found with id '{vendor_id}'.")

    def get_by_name(self, vendor_name: str) -> Vendor | None:
        normalized = vendor_name.strip().lower()
        for vendor in self.list_all():
            if vendor.name.strip().lower() == normalized:
                return vendor
        return None

    def list_all(self) -> List[Vendor]:
        return self._engine.find()

    def save(self, vendor: Vendor) -> None:
        self._engine.save(vendor, format=self._engine.preferred_format())

    def remove(self, vendor_id: str) -> None:
        try:
            vendor = self.get(vendor_id)
            path = self._engine.get_file_path(
                vendor,
                format=self._engine.preferred_format(),
            )
            self._engine.remove(path)
        except FileNotFoundError:
            pass

    def exists(self, vendor_id: str) -> bool:
        return any(vendor.id == vendor_id for vendor in self.list_all())