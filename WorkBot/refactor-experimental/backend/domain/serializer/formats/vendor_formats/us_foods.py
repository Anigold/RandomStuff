from ..csv_format import CsvFormatter
from datetime import datetime
from typing import List, Any


class USFoodsFormatter(CsvFormatter):

    def dumps(self, data: List[List[Any]], context: dict | None = None, **kwargs):

        headers = [
            'CUSTOMER NUMBER', 'DISTRIBUTOR', 'DEPARTMENT', 'DATE', 'PO NUMBER',
            'PRODUCT NUMBER', 'CUST PROD #', 'DESCRIPTION', 'BRAND', 'PACK SIZE',
            'CS PRICE', 'EA PRICE', 'CS', 'EA', 'EXTENDED PRICE', 'ORDER #',
            'STOCK STATUS', 'EXCEPTIONS / AUTO-SUB', 'SHORTED'
        ]

        store_name  = context.get('store', '')
        vendor_info = context.get('vendor_info', None)
        date_str    = context.get('date_str', datetime.now().strftime('%m/%d/%Y'))
        
        # Lookup store_id from vendor_info if possible
        store_id = '000000'
        if vendor_info and hasattr(vendor_info, 'store_ids'):
            store_id = vendor_info.store_ids.get(store_name, '000000')

        rows = [[
            store_id,            # CUSTOMER NUMBER
            '2195',              # DISTRIBUTOR
            '0',                 # DEPARTMENT
            date_str,            # DATE
            store_name,          # PO NUMBER
            i[0],                # PRODUCT NUMBER
            '', '', '', '',      # CUST PROD #, DESCRIPTION, BRAND, PACK SIZE
            '', '',              # CS PRICE, EA PRICE
            int(i[2]),           # CS
            '0',                 # EA
            '', '', '', ''       # EXTENDED PRICE, ORDER #, STOCK STATUS, etc.
        ] for i in data['rows']]

        return super().dumps({'headers': headers, 'rows': rows})