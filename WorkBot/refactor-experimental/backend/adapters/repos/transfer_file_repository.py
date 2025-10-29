from backend.app.ports.repos import TransferRepository
from pathlib import Path
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore

from backend.domain.models import Transfer
from backend.domain.serializer.serializers.transfer import TransferSerializer
from backend.domain.naming.transfer_namer import TransferFilenameStrategy

from typing import List
from backend.infra.logger import Logger

@Logger.attach_logger
class TransferFileRepository(TransferRepository):

    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Transfer](
            store=LocalBlobStore(),
            serializer=TransferSerializer(),
            namer=TransferFilenameStrategy(transfers_base_dir=base_dir),
        )

    def save(self, transfer: Transfer) -> None:
        self._engine.save(transfer, format='xlsx')

    def list_all(self) -> List[Transfer]:
        self.logger.info([self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")])
        return [self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")]
    