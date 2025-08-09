from .base_format import BaseFormat
from pathlib import Path
from typing import Any
import csv
from io import StringIO

class CSVFormat(BaseFormat):
    
    default_suffix = ".csv"

    def write(self, headers: list[str], rows: list[list[Any]]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()

    def read(self, file_path: Path) -> list[list[Any]]:
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip headers
            return [row for row in reader]
