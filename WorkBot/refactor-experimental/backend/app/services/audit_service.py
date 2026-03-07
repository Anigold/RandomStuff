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


@dataclass
class AuditServices:

    repo: AuditRepository
    downloads: DownloadManagerPort

    def __post_init__(self) -> None:
        
        self.list_transfers = ListAudits(self.repo)
        self.save_transfer  = SaveAudit(self.repo)
        self.archive_transfer = ArchiveAudit(self.repo)
        
        self.ingest_downloaded_file = IngestDownloadedFile(self.repo)