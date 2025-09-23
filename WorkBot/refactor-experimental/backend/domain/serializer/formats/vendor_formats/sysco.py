# from .base_adapter import BaseAdapter

# class SyscoAdapter(BaseAdapter):

#     preferred_format = 'csv'

#     def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
#         # Sysco expects no header row
#         return []

#     def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
#         return ['P', item.sku, int(item.quantity), 0]

from typing import Any, List
from backend.domain.serializer.formats.csv_format import CsvFormatter

class SyscoFormatter(CsvFormatter):
    """Sysco-specific CSV format with extra columns."""

    def dumps(self, data: List[List[Any]], context: dict | None = None, **kwargs) -> bytes:
        rows = [['P', i.sku, int(i.quantity), 0] for i in data['rows']]
        return super().dumps({'headers': [], 'rows': rows})
