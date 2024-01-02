import json

STORE_VENDOR_MAPPINGS = './OrderManagerMappings.json'

class OrderManager:

    def __init__(self, store: str, vendor: str):
        self.store = store
        self.vendor = vendor

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

    


    