# exporters/adapters/usfoods_export_adapter.py

from .exporter_adapter import ExportAdapter
from datetime import datetime

@ExportAdapter.register("US Foods")
class USFoodsAdapter(ExportAdapter):

    preferred_format = 'csv'

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return [
            'CUSTOMER NUMBER', 'DISTRIBUTOR', 'DEPARTMENT', 'DATE', 'PO NUMBER',
            'PRODUCT NUMBER', 'CUST PROD #', 'DESCRIPTION', 'BRAND', 'PACK SIZE',
            'CS PRICE', 'EA PRICE', 'CS', 'EA', 'EXTENDED PRICE', 'ORDER #',
            'STOCK STATUS', 'EXCEPTIONS / AUTO-SUB', 'SHORTED'
        ]


    def modify_row(self, row: list = None, item: object = None, context: dict = None) -> list:
        store_name = context.get("store", "")
        vendor_info = context.get("vendor_info", None)
        date_str = context.get("date_str", datetime.now().strftime('%m/%d/%Y'))

        # Lookup store_id from vendor_info if possible
        store_id = "000000"
        if vendor_info and hasattr(vendor_info, "store_ids"):
            store_id = vendor_info.store_ids.get(store_name, "000000")

        return [
            store_id,            # CUSTOMER NUMBER
            '2195',              # DISTRIBUTOR
            '0',                 # DEPARTMENT
            date_str,            # DATE
            store_name,          # PO NUMBER
            item.sku,            # PRODUCT NUMBER
            '', '', '', '',      # CUST PROD #, DESCRIPTION, BRAND, PACK SIZE
            '', '',              # CS PRICE, EA PRICE
            int(item.quantity),  # CS
            '0',                 # EA
            '', '', '', ''       # EXTENDED PRICE, ORDER #, STOCK STATUS, etc.
        ]
