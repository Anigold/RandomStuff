# from .base_adapter import BaseAdapter

# class HillNMarkesAdapter(BaseAdapter):

#     def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
#         return ['Key Word', 'Quantity']

#     def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
#         return [item.sku, item.quantity]

from typing import Any, List
from backend.domain.serializer.formats.excel_format import ExcelFormatter

class HillNMarkesFormatter(ExcelFormatter):

    def dumps(self, data: List[List[Any]], **kwargs) -> bytes:
        headers = ['Key Word', 'Quantity']
        rows = [[i.sku, i.quantity] for i in data]
        return super().dumps(headers + rows, **kwargs)