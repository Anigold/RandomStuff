from backend.app.ports.repos import AuditRepository
from pathlib import Path
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.infra.filesystem.local_blob_store import LocalBlobStore

from backend.domain.models import Audit
from backend.domain.serializer.serializers.audit import AuditSerializer
from backend.domain.naming.audit_namer import AuditFilenameStrategy

from backend.infra.logger import Logger

@Logger.attach_logger
class AuditFileRepository(AuditRepository):

    def __init__(self, base_dir: Path, archive_dir: Path):
        self._engine = GenericFileAdapter[Audit](
            store=LocalBlobStore(),
            serializer=AuditSerializer(),
            namer=AuditFilenameStrategy(
                audits_base_dir=base_dir, 
                archive_dir=archive_dir
            ),
        )

    def save(self, audit: Audit) -> None:
        self._engine.save(audit, format='xlsx')

    def list_all(self) -> list[Audit]:
        self.logger.info([self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")])
        return [self._engine.read_from_path(p) for p in self._engine.list_files("*.xlsx")]
    
    def archive_audit(self, audit: Audit) -> None:
        audit_file_path = self._engine.get_file_path(audit, format='xlsx')
        archive_path_excel = self._engine.get_file_path(audit, format='xlsx', category='archive')
        self._engine.move(audit_file_path, archive_path_excel, overwrite=True)
