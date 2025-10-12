from typing import Any, List
from backend.domain.serializer.formats.csv_format import CsvFormatter

class SyscoFormatter(CsvFormatter):
    """Sysco-specific CSV format with extra columns."""
    
    def dumps(self, data: List[List[Any]], context: dict | None = None, **kwargs) -> bytes:
        rows = [['P', i[0], int(i[2]), 0] for i in data['rows']]
        return super().dumps({'headers': [], 'rows': rows})
