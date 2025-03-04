from .VendorBot import VendorBot, SeleniumBotMixin, PricingBotMixin
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from openpyxl import Workbook
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from csv import writer, reader as csv_reader
from pprint import pprint

class SyscoBot(VendorBot, SeleniumBotMixin, PricingBotMixin):

    def __init__(self, driver: webdriver = None, username: str = None, password: str = None) -> None:
        VendorBot.__init__(self)
        SeleniumBotMixin.__init__(self, driver, username, password)

        self.name                 = "Sysco"
        self.minimum_order_amount = 500_00

        self.store_ids = {
            'BAKERY': 'ITHACA BAKERY',
            'COLLEGETOWN': 'COLLEGETOWN BAGELS',
            'DOWNTOWN': 'DOWNTWON COLLEGETOWN BAGELS',
            'EASTHILL': 'EAST HILL COLLEGE AVE CTBAGELS',
            'TRIPHAMMER': 'TRIPHAMMER ITHACA BAKERY'
        }

        self.special_cases = {
            '2700171': {'unit': 'EA', 'pack': 66}, # Croissant - Butter
        }

    def login(self) -> None:
        self.driver.get('https://shop.sysco.com/auth/login')

        time.sleep(10)
        email_input = self.driver.find_element(By.NAME, 'email')
        email_input.send_keys(self.username)
        
        next_button = self.driver.find_element(By.CLASS_NAME, 'login_next_button')
        next_button.click()

        time.sleep(6)

        #username_input = self.driver.find_element(By.ID, 'okta-signin-username')
        password_input = self.driver.find_element(By.ID, 'okta-signin-password')

        #username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        submit_button = self.driver.find_element(By.ID, 'okta-signin-submit')
        submit_button.click()

        time.sleep(10)

        self.is_logged_in = True
        return
    
    def logout(self) -> None:
        pass
    
    def switch_store(self, store_id: str) -> None:
        location_dropdown = self.driver.find_element(By.CLASS_NAME, 'account-flyout-opener')
        if location_dropdown.text != store_id:
            location_dropdown.click()
            time.sleep(3)
            store_selection = self.driver.find_element(By.ID, 'searched_accounts_container')
            store_locations = store_selection.find_elements(By.CLASS_NAME, 'customer-info')
            '''
            Still haven't figured this one out:

            The page seems to reload the frame with a different class name as soon as you interact with it.
            Something about referencing the element with Selenium triggers this effect without explicit
            interaction.

            Hence the above useless variable declaration.
            '''
            store_locations_postupdate = self.driver.find_elements(By.CLASS_NAME, 'customer-name')
            location = [i for i in store_locations_postupdate if store_id == i.text][0]
            location.click()
        return
    
    def format_for_file_upload(self, item_data: dict, path_to_save: str, store: str) -> None:

        with open(f'{path_to_save}.csv', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file)

            for item in item_data:
                quantity = item['quantity']
                sku      = item['sku']
                csv_writer.writerow(['P', sku, int(quantity), 0])

        return
    
    def retrieve_pricing_sheet(self, guide_name: str) -> str:
        
        if not self.is_logged_in:
            self.login()
       
        # Make sure we're on the Ithaca Bakery location
        location_dropdown = self.driver.find_element(By.CLASS_NAME, 'account-flyout-opener')
        if location_dropdown.text != self.store_ids['BAKERY']:
            self.switch_store(self.store_ids['BAKERY'])
            time.sleep(5)

        # Go to lists
        self.driver.get('https://shop.sysco.com/app/lists/purchase-history')
        time.sleep(15)

        try:
            redirect_popup = self.driver.find_element(By.CLASS_NAME, 'dashboard-redirect-modal')
            close_modal = redirect_popup.find_element(By.CLASS_NAME, 'marketing-modal-close-btn ')
            close_modal.click()
            time.sleep(6)
            self.driver.get('https://shop.sysco.com/app/lists/purchase-history')
            
        except:
            pass
        
        time.sleep(6)
        input('Click enter when ready')
        # Choose the correct list
        list_container = self.driver.find_element(By.CLASS_NAME, 'list-navigation-sidebar')
        lists = list_container.find_elements(By.CLASS_NAME, 'list-navigation-item')
        list_to_download = [i for i in lists if guide_name == i.text][0]
        list_to_download.click()

        time.sleep(4)

        # Export the list
        content_area = self.driver.find_element(By.XPATH, './/div[@class="myProducts-content myProducts-content-list-nav"]')

        more_actions_button_container = content_area.find_element(By.XPATH, './/div[@class="fd more-actions-wrapper"]')
        more_actions = more_actions_button_container.find_element(By.XPATH, './/button[@data-id="more-actions-btn"]')
        more_actions.click()                  

        time.sleep(2)
        
        export_button = self.driver.find_element(By.XPATH, './/li[@data-id="export-list-btn"]')
        export_button.click()

        time.sleep(8)

        # The export modal seemingly gets reloaded after every interaction leading to stale references. I've skipped it entirely.
        # export_modal = self.driver.find_element(By.CLASS_NAME, 'modal-body')
        file_name = self.driver.find_element(By.XPATH, './/input[@data-id="export-list-modal-file-name-input"]')
        file_name.send_keys(Keys.BACKSPACE * 40)
        filename = f'Sysco {guide_name}'
        file_name.send_keys(filename)

        time.sleep(3)

        pricing_toggle = self.driver.find_element(By.CLASS_NAME, 'toggle-wrapper')
        pricing_toggle.click()

        time.sleep(1)

        submit_export = self.driver.find_element(By.XPATH, './/button[@data-id="export-list-modal-export-btn"]')
        submit_export.click()

        time.sleep(10)

        return f'{filename}.csv'
    
    def get_pricing_info_from_sheet(self, path_to_pricing_sheet: str) -> dict:
        item_info = {}
        with open(path_to_pricing_sheet) as sysco_info:
            reader = csv_reader(sysco_info, delimiter=',')
            for pos, row in enumerate(reader):

                if pos < 2: continue

                item_sku 		= row[1]
                item_name 		= row[12]
                quantity, units = PricingBotMixin.helper_format_size_units(row[7], row[8])
                cost 			= float(row[14]) if row[14] != '' else float(row[15])

                if item_sku in self.special_cases:
                    quantity, units = PricingBotMixin.helper_format_size_units(self.special_cases[item_sku]['pack'], self.special_cases[item_sku]['unit'])

                if item_name not in item_info:
                    item_info[item_name] = {
                        'SKU': item_sku,
                        'quantity': quantity,
                        'units': PricingBotMixin.normalize_units(units),
                        'cost': cost,
                        'case_size': f'{row[7]} / {row[8]}'
                    }
        pprint(item_info)
        return item_info