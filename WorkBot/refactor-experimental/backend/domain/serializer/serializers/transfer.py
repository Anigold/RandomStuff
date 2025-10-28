# backend/domain/serializers/vendor_serializer.py

from pathlib import Path
from typing import Any, Dict, Optional
import json
from backend.domain.models import Transfer
from backend.app.ports.generic import Serializer
from ..formats import get_formatter 
from backend.infra.logger import Logger

@Logger.attach_logger
class TransferSerializer(Serializer[Transfer]):

    def __init__(self, default_format: str = 'json'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        ...

    # ----------------- Dumps -----------------
    def dumps(self, obj: Transfer, format: Optional[str] = None) -> bytes:
        ...

    # ----------------- Loads -----------------
    def loads(self, data: bytes, format: Optional[str] = None) -> Transfer:
        ...

    def load_path(self, path: Path, context: dict | None = None) -> Transfer:
        ...

        # -------- Domain <-> dict --------
    def to_dict(self, store: Transfer) -> Dict[str, Any]:
        ...

    def from_dict(self, data: Dict[str, Any]) -> Transfer:
        ...

    # -------- Domain <-> tabular --------
    def _to_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def from_table(self, table: Dict[str, Any]) -> Transfer:
        ...
