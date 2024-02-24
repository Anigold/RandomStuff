from .VendorBot import VendorBot
from csv import writer
class UNFIBot(VendorBot):

    def __init__(self, driver, username, password):
        super().__init__()
        self.name     = 'UNFI'
        self.driver   = driver
        self.username = username
        self.password = password

    def format_for_file_upload(self, item_data: dict, path_to_save: str) -> None:
        
        with open(f'{path_to_save}.csv', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file)
            fields = ['Item Code', 'Quantity']

            csv_writer.writerow(fields)

            for sku in item_data:
                quantity = item_data[sku]['quantity']
                csv_writer.writerow([sku, int(quantity)])

        return

            