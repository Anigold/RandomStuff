from .VendorBot import VendorBot
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from openpyxl import Workbook
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from csv import writer

class SyscoBot(VendorBot):

    def __init__(self, driver: webdriver, username, password) -> None:
        super().__init__()
        self.name = "Sysco"
        self.driver = driver
        self.username = username
        self.password = password

        self.store_ids = {}

    def login(self) -> None:
        pass

    def logout(self) -> None:
        pass
    
    def switch_store(self, store_id: str) -> None:
        pass

    def format_for_file_upload(self, item_data: dict, path_to_save: str) -> None:

        with open(f'{path_to_save}.csv', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file)

            for sku in item_data:
                quantity = item_data[sku]['quantity']
                csv_writer.writerow(['P', sku, int(quantity), 0])

        return
    
    def retrieve_pricing_sheet(self, guide_name: str) -> None:
       pass

    def end_session(self) -> None:
        self.driver.close()
        return