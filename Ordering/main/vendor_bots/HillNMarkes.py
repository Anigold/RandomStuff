from .VendorBot import VendorBot
from selenium.webdriver.common.by import By
import time
from pprint import pprint

class HillNMarkes(VendorBot):

    def __init__(self, driver, username, password, order_manager):
        self.driver    = driver
        self.username  = username
        self.password  = password
        self.order_manager = order_manager
        self.store_ids = {
            'BAKERY': 0,
            'COLLEGETOWN': 1,
            'TRIPHAMMER': 4,
            'EASTHILL': 5,
            'DOWNTOWN': 9
        }

    def login(self) -> None:
	
        self.driver.get('https://www.hillnmarkes.com/Welcome.action')
        time.sleep(5)

        print('Finding login dropdown...')
        login_dropdown_button = self.driver.find_elements(By.CLASS_NAME, 'dropdown-toggle')
        login_dropdown_button[0].click()
        print('...login dropdown found.')

        print('')
        time.sleep(2)

        print('Finding login form...')
        login_form    = self.driver.find_element(By.ID, 'popLoginForm')
        username_form = self.driver.find_element(By.ID, 'popUserName')
        password_form = self.driver.find_element(By.ID, 'popPassword')
        print('...login form found.')

        print('')

        print('Sending login information...')
        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        login_form.find_element(By.XPATH, './/button[@type="submit"]').click()
        print('...credentials sent.')

        time.sleep(10)
        print('')

        print('Selecting store...')
        store_selection_table = self.driver.find_element(By.ID, 'example')
        store_rows            = store_selection_table.find_elements(By.XPATH, './/tbody/tr')

        # Choosing IB for testing
        store_rows[0].find_element(By.XPATH, './/td').click()
        time.sleep(10)
        print('...store selected.')

        print('')

        print('Waiting for login success...')

        return

    def go_to_quick_cart_file_upload(self) -> None:
        self.driver.get('https://www.hillnmarkes.com/QuickCartStandard')
        return
        
    def upload_quick_cart_file(self, file_to_upload: str) -> None:

        if self.driver.current_url != 'https://www.hillnmarkes.com/QuickCartStandard':
            self.go_to_quick_cart_file_upload()
            time.sleep(5)
            return self.upload_quick_cart_file(file_to_upload)

        quick_order_tab = self.driver.find_element(By.ID, 'quickOrderTab')
        file_upload_tab = quick_order_tab.find_elements(By.XPATH, './/ul/li')[2]
        file_upload_tab.click()

        time.sleep(2)

        file_upload_form  = self.driver.find_element(By.ID, 'uploadForm')
        file_upload_input = self.driver.find_element(By.ID, 'datafile')
        file_upload_input.send_keys(file_to_upload)
        time.sleep(5)
        file_submit = file_upload_form.find_element(By.XPATH, './input[@value="Upload"]')
        attrs = self.driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', file_submit)
        pprint(attrs)
        file_submit.click()
        time.sleep(30)
        return

    def switch_store(self, store: str) -> None:

        if store not in self.store_ids:
            return
        
        my_account_button = self.driver.find_element(By.XPATH, './/a[@data-target="myAccountMenu"]')
        my_account_button.click()
        time.sleep(1)

        my_account_menu       = self.driver.find_element(By.CLASS_NAME, 'myAccountMenu')
        account_menu_choices  = my_account_menu.find_elements(By.TAG_NAME, 'li')
        change_account_button = account_menu_choices[2]
        change_account_button.click()
        time.sleep(5)

        store_change_table = self.driver.find_element(By.ID, 'example')
        store_change_rows  = store_change_table.find_elements(By.TAG_NAME, 'tr')
        store_to_change_to = store_change_rows[self.store_ids[store]]

        row_data                = store_to_change_to.find_elements(By.TAG_NAME, 'td')
        change_to_button_column = row_data[0]
        change_to_button        = change_to_button_column.find_element(By.TAG_NAME, 'label')
        change_to_button.click()
        time.sleep(7)

        return

    def format_for_file_upload(self, file_to_format: str) -> None:
        pass