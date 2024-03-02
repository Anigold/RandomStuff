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

class SyscoBot(VendorBot):

    def __init__(self, driver: webdriver, username, password) -> None:
        super().__init__()
        self.name = "Sysco"
        self.driver = driver
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.store_ids = {
            'BAKERY': 'ITHACA BAKERY',
            'COLLEGETOWN': 'COLLEGETOWN BAGELS',
            'DOWNTOWN': 'DOWNTWON COLLEGETOWN BAGELS',
            'EASTHILL': 'EAST HILL COLLEGE AVE CTBAGELS',
            'TRIPHAMMER': 'TRIPHAMMER ITHACA BAKERY'
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
    
    def format_for_file_upload(self, item_data: dict, path_to_save: str) -> None:

        with open(f'{path_to_save}.csv', 'w', newline='') as csv_file:

            csv_writer = writer(csv_file)

            for sku in item_data:
                quantity = item_data[sku]['quantity']
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
        self.driver.get('https://shop.sysco.com/app/lists')
        time.sleep(5)

        # Choose the correct list
        list_container = self.driver.find_element(By.CLASS_NAME, 'list-navigation-sidebar')
        lists = list_container.find_elements(By.CLASS_NAME, 'list-navigation-item')
        list_to_download = [i for i in lists if guide_name == i.text][0]
        list_to_download.click()

        time.sleep(4)

        # Export the list
        more_actions_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[5]/div/div/div/div[2]/div[3]/div[2]/div/div[3]/div/button/div/div')
        more_actions_button.click()

        export_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[5]/div/div/div/div[2]/div[3]/div[2]/div/div[3]/div/div/li[2]')
        export_button.click()

        time.sleep(2)

        # The export modal seemingly gets reloaded after every interaction leading to stale references. I've skipped it entirely.
        # export_modal = self.driver.find_element(By.CLASS_NAME, 'modal-body')
        file_name = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[10]/div[1]/div/div/div[2]/div[1]/div[1]/div/input')
        file_name.send_keys(Keys.BACKSPACE * 40)
        filename = f'Sysco {guide_name}'
        file_name.send_keys(filename)

        time.sleep(3)

        pricing_toggle = self.driver.find_element(By.CLASS_NAME, 'toggle-wrapper')
        pricing_toggle.click()

        time.sleep(1)

        submit_export = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div[10]/div[1]/div/div/div[3]/button[2]')
        submit_export.click()

        time.sleep(3)

        return f'{filename}.csv'
    
    def end_session(self) -> None:
        self.driver.close()
        return