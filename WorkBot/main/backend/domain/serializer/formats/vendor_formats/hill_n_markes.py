from typing import Any, List
from backend.domain.serializer.formats.excel_format import ExcelFormatter

class HillNMarkesFormatter(ExcelFormatter):
    
    def dumps(self, data: List[List[Any]], **kwargs) -> bytes:
        headers = ['Key Word', 'Quantity']
        rows = [[i[0], i[2]] for i in data['rows']] # Need to normalize to fix arbitrary indexing
        return super().dumps({'headers': headers, 'rows': rows})