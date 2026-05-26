from backend.domain.serializer.formats.csv_format import CsvFormatter
from typing import List, Any


class AlbertsOrganicsFormatter(CsvFormatter):
    
    def dumps(self, data: List[List[Any]], context: dict | None = None, **kwargs) -> bytes:
        headers = ['Item Code', 'Quantity']
        rows = [[i[0], float(i[2])] for i in data['rows']]
        return super().dumps({'headers': headers, 'rows': rows})
