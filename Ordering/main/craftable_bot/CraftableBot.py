from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
import time
import keyboard

'''
Craftable Bot utlizes Selenium to interact with the Craftable website. 
'''
class CraftableBot:

    def __init__(self, driver, username, password):
        self.driver    = driver
        self.username  = username
        self.password  = password

        self.is_logged_in = False
        self.stores = {
            'BAKERY': '14376',
            'DOWNTOWN': '14373',
            'EASTHILL': '14374',
            'TRIPHAMMER': '14375',
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
            row_vendor_name = row_data[3].text
         
            if date == row_date.text and pos not in completed_orders:
                
                row_date.click()
                time.sleep(4)

                download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
                ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
                time.sleep(5)

                open_tabs = self.driver.window_handles
                self.driver.switch_to.window(open_tabs[1])
                time.sleep(2)

                keyboard.press_and_release('ctrl+s')
                time.sleep(3)
                keyboard.write(f'{row_vendor_name} - {store} {date.replace("/", "")}.pdf')
                time.sleep(2)
                keyboard.press('enter')
                time.sleep(2)
                keyboard.press_and_release('ctrl+w')
                time.sleep(2)

                self.driver.switch_to.window(open_tabs[0])
                self.driver.back()
                time.sleep(3)

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
            row_vendor_name = row_data[3].text
         
            if pos not in completed_orders:
                
                row_date.click()
                time.sleep(4)

                download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
                ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
                time.sleep(5)

                open_tabs = self.driver.window_handles
                self.driver.switch_to.window(open_tabs[1])
                time.sleep(2)

                keyboard.press_and_release('ctrl+s')
                time.sleep(3)
                keyboard.write(f'{row_vendor_name} - {store} {date.replace("/", "")}.pdf')
                time.sleep(2)
                keyboard.press('enter')
                time.sleep(2)
                keyboard.press_and_release('ctrl+w')
                time.sleep(2)

                self.driver.switch_to.window(open_tabs[0])
                self.driver.back()
                time.sleep(3)