from backend.app.ports.repos import TransferRepository
from pathlib import Path
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore

from backend.domain.models import Transfer
from backend.domain.serializer.serializers.transfer import TransferSerializer
from backend.domain.naming.transfer_namer import TransferFilenameStrategy



class TransferFileRepository(TransferRepository):

    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Transfer](
            store=LocalBlobStore(),
            serializer=TransferSerializer(),
            namer=TransferFilenameStrategy(base=base_dir),
        )

    def save(self, transfer: Transfer) -> None:
        ...