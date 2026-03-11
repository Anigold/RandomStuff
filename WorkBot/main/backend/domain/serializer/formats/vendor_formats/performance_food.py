from ..txt_format import TxtFormatter
from typing import List, Any

class PerformanceFoodFormatter(TxtFormatter):

    def dumps(self, data: List[List[Any]], context: dict | None = None, **kwargs) -> bytes:
        rows = [[i[0], int(i[2]), 'CS'] for i in data['rows']]
        return super().dumps({'headers': [], 'rows': rows})
