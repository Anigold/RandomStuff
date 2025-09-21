# backend/app/formatters/csv_formatter.py

from io import StringIO
from pathlib import Path
from typing import Any, Dict, List
import csv
from .base_format import BaseFormatter


class CsvFormatter(BaseFormatter):
    """Domain-agnostic CSV formatter: expects a dict with 'headers' and 'rows'."""

    def format_name(self) -> str:
        return "csv"

    def dumps(self, obj: Dict[str, Any]) -> bytes:
        """
        obj should be of the form:
        {
            "headers": ["col1", "col2", ...],
            "rows": [
                ["a", "b", ...],
                ["c", "d", ...],
            ]
        }
        """
        buf = StringIO()
        writer = csv.writer(buf)

        headers = obj.get("headers", [])
        rows = obj.get("rows", [])

        if headers:
            writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

        return buf.getvalue().encode("utf-8")

    def loads(self, data: bytes) -> Dict[str, Any]:
        buf = StringIO(data.decode("utf-8"))
        reader = csv.reader(buf)
        rows = list(reader)

        if not rows:
            return {"headers": [], "rows": []}

        headers, *body = rows
        return {"headers": headers, "rows": body}

    def load_path(self, path: Path) -> Dict[str, Any]:
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return {"headers": [], "rows": []}

        headers, *body = rows
        return {"headers": headers, "rows": body}
