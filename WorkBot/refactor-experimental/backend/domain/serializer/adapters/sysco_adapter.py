from .base_adapter import BaseAdapter

class SyscoAdapter(BaseAdapter):

    preferred_format = 'csv'

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        # Sysco expects no header row
        return []

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return ['P', item.sku, int(item.quantity), 0]



# backend/domain/serializer/vendor_formatters/sysco_formatter.py
from typing import Any, List
from backend.domain.serializer.formatters.csv_formatter import CsvFormatter

class SyscoFormatter(CsvFormatter):
    """Sysco-specific CSV format with extra columns."""

    def dumps(self, data: List[List[Any]], **kwargs) -> bytes:
        # Add Sysco-required header row
        sysco_header = [] # No header row
        data_with_header = [sysco_header] + data

        # Add a blank "CustomField" column for each row
        augmented_data = [row + [""] for row in data]

        return super().dumps([sysco_header] + augmented_data, **kwargs)
