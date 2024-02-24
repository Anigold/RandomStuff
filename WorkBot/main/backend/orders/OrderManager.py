import json
from ..vendor_bots import VendorBot
STORE_VENDOR_MAPPINGS = './OrderManagerMappings.json'

class OrderManager:

    def __init__(self, store: str, vendors: list):
        self.store  = store
        self.vendor = vendors

    '''
    Get the vendor ID for our current store.
    '''
    def get_vendor_id(self) -> str:
        with open(STORE_VENDOR_MAPPINGS, 'r') as sv_mappings:
            data = json.load(sv_mappings)

            # This is not efficient, but N < 10 so we don't care.
            for store in data['stores']:
                if store['store_name'] == self.store:
                    for vendor in enumerate(store['vendors']):
                        if vendor['vendor_name'] == self.vendor:
                            return vendor['vendor_store_id']

    def convert_craftable_pdf_to_vendor_format(self, path: str, vendor: VendorBot) -> None:
        order_sheets = get_files(f'{path}')
	
        for order_sheet in order_sheets:

            output = StringIO()
            
            # Extract PDF text to string builder
            convert_to_html(join(path, order_sheet), output)

            # Convert PDF text to HTML page
            with open(f'{path}temp{order_sheet.split(".")[0]}.html', 'w') as html_file:
                html_file.write(output.getvalue())

            # Parse HTML page
            with open(f'{path}temp{order_sheet.split(".")[0]}.html') as fp:
                column_info = extract_table_column_data(fp, {'item_skus': {'styles': 'left:52px'}, 'item_quantities': {'styles': 'left:352px'}})
                
            items = retrieve_item_ordering_information(column_info)

            workbook = vendor.format_for_file_upload(items, f'{path}{order_sheet.split(".")[0]}')
            
            

            remove(join(path, f'temp{order_sheet.split(".")[0]}.html'))


    