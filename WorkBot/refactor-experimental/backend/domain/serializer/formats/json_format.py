import json
from pathlib import Path
from typing import Any, Dict
from .base_format import BaseFormatter

class JSONFormatter(BaseFormatter[Dict[str, Any]]):
    """Domain-agnostic JSON formatter: expects a dict with 'headers' and 'rows'."""

    def format_name(self) -> str:
        return "json"

    def dumps(self, obj: Dict[str, Any], format: str = None) -> bytes:
        return json.dumps(obj, indent=2).encode("utf-8")

    def loads(self, data: bytes, format: str = None) -> Dict[str, Any]:
        return json.loads(data.decode("utf-8"))

    def load_path(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
