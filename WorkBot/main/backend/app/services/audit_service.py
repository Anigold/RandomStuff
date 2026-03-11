from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    DownloadManagerPort,
    AuditRepository
)


from dataclasses import dataclass
from typing import Optional, Callable, List


from backend.domain.models import Audit

from backend.infra.logger import Logger
from pathlib import Path

# ========== QUERIES ==========

@Logger.attach_logger
@dataclass(frozen=True)
class ListAudits:

    repo: AuditRepository

    def __call__(self) -> List[Audit]:
        self.logger.info('Listing all audits.')
        return self.repo.list_all()

    
@Logger.attach_logger
@dataclass(frozen=True)
class SaveAudit:

    repo: AuditRepository

    def __call__(self, audit: Audit) -> Audit:
        return self.repo.save(audit)
    

@Logger.attach_logger
@dataclass(frozen=True)
class ArchiveAudit:

    repo: AuditRepository

    def __call__(self, audit: Audit) -> None:
        self.logger.info(f'Archiving transfer: {audit}')
        self.repo.archive_audit(audit)

@Logger.attach_logger
@dataclass(frozen=True)
class IngestDownloadedFile:

    repo: AuditRepository

    def __call__(self, audit: Audit, file_path: Path, kind: str = 'pdf') -> None:

        self.repo.ingest_downloaded_file(
            audit=audit,
            src_path=file_path,
            kind=kind,
        )

@Logger.attach_logger
@dataclass(frozen=True)
class ImportDownloadedAudit:

    repo: AuditRepository

    def __call__(self, file_path: Path, hints: dict | None = None, source: str | None = 'audit') -> Audit:
        return self.repo.import_downloaded_audit(src_path=file_path, hints=hints, source=source)

@dataclass
class AuditServices:

    repo: AuditRepository

    def __post_init__(self) -> None:
        
        self.list_transfers = ListAudits(self.repo)
        self.save_transfer  = SaveAudit(self.repo)
        self.archive_transfer = ArchiveAudit(self.repo)
        
        self.ingest_downloaded_file = IngestDownloadedFile(self.repo)
        self.import_downloaded_audit = ImportDownloadedAudit(self.repo)

    def ingest_downloaded_audit(self, file_path: Path, hints: dict, source: str | None = None) -> Audit:
        audit = self.parser.parse_metadata(file_path=file_path, hints=hints)
        self.save_audit(audit)
        self.ingest_downloaded_file(audit, file_path, kind="xlsx")
        return audit