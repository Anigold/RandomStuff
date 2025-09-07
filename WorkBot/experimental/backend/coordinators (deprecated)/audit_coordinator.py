from backend.storage.file.download_handler import DownloadHandler
from backend.models.audit import Audit

class AuditCoordinator:

    def __init__(self):
        self.file_handler     = None
        self.db_handler       = None
        self.download_handler = DownloadHandler()

    def get_audit(self, store: str, start_date: str, end_date: str, audit_type: str) -> Audit:
        pass