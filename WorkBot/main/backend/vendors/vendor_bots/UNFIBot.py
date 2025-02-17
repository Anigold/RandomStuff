from .VendorBot import VendorBot, SeleniumBotMixin
from csv import writer
class UNFIBot(VendorBot, SeleniumBotMixin):

    def __init__(self):
        super().__init__()

        self.name                 = 'UNFI'
        self.minimum_order_amount = 1_500_00 # $1500 in cents


    def format_for_file_upload(self, item_data: dict, path_to_save: str) -> None:
        
        with open(f'{path_to_save}.csv', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file)
            fields = ['Item Code', 'Quantity']

            csv_writer.writerow(fields)

            for sku in item_data:
    
                # sku = item_data[name]['sku']
                quantity = item_data[sku]['quantity']
                
                csv_writer.writerow([sku, int(quantity)])

        return

            