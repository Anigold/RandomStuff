from .base_adapter import BaseAdapter

class PerformanceFoodAdapter(BaseAdapter):
    preferred_format = 'csv'
    preferred_extension = 'txt'

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return []

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return [item.sku, int(item.quantity), 'CS']
