from .VendorBot import VendorBot
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from openpyxl import Workbook
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from csv import writer
from datetime import date

class PerformanceFoodBot(VendorBot):

    def __init__(self, driver: webdriver, username, password) -> None:
        super().__init__(driver, username, password)
        
        self.name               = "Performance Food"
        self.minimum_order_case = 20

        self.store_ids = {}

        

    def login(self) -> None:
        self.driver.get('https://www.customerfirstsolutions.com')

        time.sleep(4)

        username_input = self.driver.find_element(By.ID, 'signInName')
        password_input = self.driver.find_element(By.ID, 'password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        submit_button = self.driver.find_element(By.ID, 'next')
        submit_button.click()
        
        time.sleep(5)
        self.is_logged_in = True
        return

    def logout(self) -> None:
        pass
    
    def switch_store(self, store_id: str) -> None:
        pass

    def format_for_file_upload(self, item_data: dict, path_to_save: str) -> None:
        
        with open(f'{path_to_save}.txt', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file, delimiter='\t')

            for sku in item_data:
                quantity = item_data[sku]['quantity']
                
                csv_writer.writerow([sku, int(quantity), 'CS'])

        return
    
    def retrieve_pricing_sheet(self, guide_name: str) -> None:

        if not self.is_logged_in:
            self.login()
       
        # Ensure we're on the Ithaca Bakery location
        current_location = self.driver.find_element(By.CLASS_NAME, 'MuiBox-root')
        current_location_name = current_location.find_element(By.XPATH, '//span[2]')
    
        if current_location_name.text != 'Ithaca Bakery':
            time.sleep(3)
            current_location_name.click()

            time.sleep(3)

            location_dropdown = self.driver.find_element(By.XPATH, './/div[@data-testid="location-menu"]')
            location_input = location_dropdown.find_element(By.XPATH, './/input[@data-testid="location-search-menu-search"]')
            location_input.send_keys('bakery')
            location_input.send_keys(Keys.ENTER)

            time.sleep(2)

            location = location_dropdown.find_element(By.XPATH, './/span[@data-testid="location-menu-customer-name"]')
            location.click()

            time.sleep(5)

        lists_button = self.driver.find_element(By.XPATH, '//span[@data-testid="nav-item-Lists"]')
        lists_button.click()
        time.sleep(5)

        lists = self.driver.find_elements(By.XPATH, '//h5[@data-testid="product-list-management-card-name"]')
        selected_list = [i for i in lists if guide_name.upper() == i.text][0]
        selected_list.click()
        time.sleep(2)

        export_options_button = self.driver.find_element(By.XPATH, '//button[@data-testid="product-list-management-detail-menu-btn"]')
        export_options_button.click()

        time.sleep(1)

        export_button = self.driver.find_element(By.XPATH, '//div[@data-testid="product-list-menu-export-list"]')
        export_button.click()

        time.sleep(3)

        export_report_button = self.driver.find_element(By.XPATH, '//button[@data-testid="export-report-btn"]')
        export_report_button.click()

        time.sleep(8)
        today = date.today()
        today_mm_dd_yyyy = today.strftime('%m-%d-%Y')

        return f'{guide_name}_RFS Eastern PA-07110_{today_mm_dd_yyyy}.xlsx'
    
    def end_session(self) -> None:
        self.driver.close()
        return