from typing import Any, List
from backend.domain.serializer.formats.excel_format import ExcelFormatter

class HillNMarkesFormatter(ExcelFormatter):
    
    def dumps(self, data: List[List[Any]], **kwargs) -> bytes:
        headers = ['Key Word', 'Quantity']
        rows = [[i.sku, i.quantity] for i in data]
        return super().dumps(headers + rows, **kwargs)