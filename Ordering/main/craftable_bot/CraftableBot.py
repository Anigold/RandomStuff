from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
import time
from pynput.keyboard import Key, Controller
from os import rename
from os.path import join
from pprint import pprint
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv
from os import getenv

SAVE_FILE_PATH = 'C:/Users/Will/Desktop/Andrew/Projects/RandomStuff/Ordering/main/orders/OrderFiles/'
DOWNLOAD_PATH = getenv('DOWNLOAD_PATH') or 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\downloads\\'

'''
Craftable Bot utlizes Selenium to interact with the Craftable website. 
'''
class CraftableBot:

    def __init__(self, driver, username, password):
        self.driver        = driver
        self.username      = username
        self.password      = password
       # self.order_manager = order_manager

        self.is_logged_in = False
        self.stores = {
            'BAKERY':      '14376',
            'DOWNTOWN':    '14373',
            'EASTHILL':    '14374',
            'TRIPHAMMER':  '14375',
            'COLLEGETOWN': '14372',
        }

    '''
    Login to the Craftable website using the standard landing page.

    This method assumes the bot knows the username and password.

    Args:
        None

    Returns:
        None
    '''
    def login(self) -> None:

        self.driver.get('https://app.craftable.com/signin')

        time.sleep(4)
        
        login_form = self.driver.find_element(By.XPATH, './/form')
        
        fieldsets = login_form.find_elements(By.XPATH, './/fieldset')
        email_fieldset = fieldsets[0]
        password_fieldset = fieldsets[1]

        email_input = email_fieldset.find_element(By.TAG_NAME, 'input')
        password_input = password_fieldset.find_element(By.TAG_NAME, 'input')

        submit_button_div = login_form.find_elements(By.XPATH, './/button')[0]
        
        email_input.send_keys(self.username)
        password_input.send_keys(self.password)

        submit_button_div.click()
        time.sleep(5)

        self.is_logged_in = True
        return
    
    '''
    Close the driver session.

    Args:
        None

    Returns:
        None
    '''
    def close_session(self) -> None:
        self.driver.close()
        return
    
    '''
    Switch to another store's page.

    Args:
        store_code: store name

    Returns:
        None
    '''
    def switch_store(self, store: str) -> None:

        if store not in self.stores: return None

        if store == 'DIRECTOR':
            self.driver.get('https://app.craftable.com/director/2/583')
            return
        
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}')
        return

    '''
    Go to the store's order page and download the order invoices.

    Args:
        store: string name of the store

    Returns:
        None
    '''
    def get_orders(self, store: str, date: str) -> None:
        
        # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        # Find all the orders with the right date
        table_body = self.driver.find_element(By.XPATH, './/tbody')
        table_rows = table_body.find_elements(By.XPATH, './tr')

        completed_orders = [] # Store the index of the rows here
        completed_orders_names = [] # Store the name of the vendor here
        for pos, row in enumerate(table_rows):
            table_body = self.driver.find_element(By.XPATH, './/tbody')
            table_rows = table_body.find_elements(By.XPATH, './tr')
            row = table_rows[pos]
            row_data = row.find_elements(By.XPATH, './td')
            row_date = row_data[2]
            row_date_text = row_data[2].text
            row_vendor_name = row_data[3].text
         
            if date == row_date_text and pos not in completed_orders:
                
                row_date.click()
                time.sleep(4)

                download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
                ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
                time.sleep(10)

                # open_tabs = self.driver.window_handles
                # time.sleep(2)

                # self._run_save_protocol()
                # time.sleep(1)

                self._rename_new_order_file(SAVE_FILE_PATH, f'{row_vendor_name} - {store} {row_date_text.replace("/", "")}.pdf')
                
                # keyboard.type(f'{row_vendor_name} - {store} {row_date_text.replace("/", "")}.pdf')
                # time.sleep(2)


                time.sleep(2)

                #self.driver.switch_to.window(open_tabs[0])
                self.driver.back()
                time.sleep(3)

    '''
    Scrapes the order webpage of each order and saves to file.

    Developer Note: we need to do this because the order PDF files are proving to 
    be non-generally scrapable. 

    We have been converting the PDF to hardcoded HTML and then selecting elements based
    on tags and in-line styles which correspond to positions in the PDF table.

    We discovered that double-digit values in the quantity columns vary in size based
    on the integers involved; the corresponding size for "13" does not match the 
    corresponding size for "72" nor "28", etc..

    I don't want to hardcode every integer pair, so we will scrape the webpage instead.
    '''
    def get_all_orders_from_webpage(self, store: str) -> None:
         # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        # Find all the orders with the right date
        table_body = self.driver.find_element(By.XPATH, './/tbody')
        table_rows = table_body.find_elements(By.XPATH, './tr')

        completed_orders = [] # Store the index of the rows here
        completed_orders_names = [] # Store the name of the vendor here
        for pos, row in enumerate(table_rows):
            table_body = self.driver.find_element(By.XPATH, './/tbody')
            table_rows = table_body.find_elements(By.XPATH, './tr')
            row = table_rows[pos]
            row_data = row.find_elements(By.XPATH, './td')
            row_date = row_data[2]
            row_date_text = row_data[2].text
            row_vendor_name = row_data[3].text
         
            if pos not in completed_orders:
                
                row_date.click()
                WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.TAG_NAME, 'table')))
                order_table = self.driver.find_element(By.TAG_NAME, 'tbody')
                item_rows = order_table.find_elements(By.TAG_NAME, './tr')

                for item in item_rows:
                    item_info = item.find_elements(By.TAG_NAME, 'td')
                    print('found')
                    pprint.pprint(item_info)

                time.sleep(7)

      

                #self._rename_new_order_file(SAVE_FILE_PATH, f'{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.pdf')
                



                time.sleep(2)


                self.driver.back()
                time.sleep(3)
        return

    '''
    Go to the store's order page and download all the order invoices.

    Args:
        store: string name of the store

    Returns:
        None
    '''
    def get_all_orders(self, store: str) -> None:

        # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        # Find all the orders with the right date
        table_body = self.driver.find_element(By.XPATH, './/tbody')
        table_rows = table_body.find_elements(By.XPATH, './tr')

        completed_orders = [] # Store the index of the rows here
        completed_orders_names = [] # Store the name of the vendor here
        for pos, row in enumerate(table_rows):
            table_body = self.driver.find_element(By.XPATH, './/tbody')
            table_rows = table_body.find_elements(By.XPATH, './tr')
            row = table_rows[pos]
            row_data = row.find_elements(By.XPATH, './td')
            row_date = row_data[2]
            row_date_text = row_data[2].text
            row_vendor_name = row_data[3].text
         
            if pos not in completed_orders:
                
                row_date.click()
                time.sleep(4)

                download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
                ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
                time.sleep(7)

      

                self._rename_new_order_file(DOWNLOAD_PATH, f'{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.pdf')
                



                time.sleep(2)


                self.driver.back()
                time.sleep(3)

    def get_orders_from_vendor(self, store: str) -> None:
        pass
    
    def _rename_new_order_file(self, path:str, file_name:str) -> None:
     
        rename(f'{path}Order.pdf', f'{SAVE_FILE_PATH}{file_name}')
        return
    
    def _run_save_protocol() -> None:
        keyboard = Controller()

        keyboard.press(Key.ctrl)
        keyboard.press('s')
        keyboard.release(Key.ctrl)
        keyboard.release('s')

        time.sleep(2)
              
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        return