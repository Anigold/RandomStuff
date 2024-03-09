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
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
from os import getenv
import pprint

from openpyxl import Workbook

from backend.transferring import Transfer
import calendar

ORDER_FILES_PATH = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\orders\\OrderFiles\\'
PRICING_FILES_PATH = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\pricing\\VendorSheets\\'
DOWNLOAD_PATH = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\downloads\\'

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

        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, './/form')))
        
        login_form = self.driver.find_element(By.XPATH, './/form')
        
        fieldsets = login_form.find_elements(By.XPATH, './/fieldset')
        email_fieldset = fieldsets[0]
        password_fieldset = fieldsets[1]

        email_input = email_fieldset.find_element(By.XPATH, './/input')
        password_input = password_fieldset.find_element(By.XPATH, './/input')

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
    def get_all_orders_from_webpage(self, store: str, download_pdf=False) -> None:
        # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        # Find all the orders with the right date
        table_body = self.driver.find_element(By.XPATH, './/tbody')
        table_rows = table_body.find_elements(By.XPATH, './tr')

        completed_orders = [] # Store the index of the rows here
        for pos, row in enumerate(table_rows):
            table_body      = self.driver.find_element(By.XPATH, './/tbody')
            table_rows      = table_body.find_elements(By.XPATH, './tr')
            row             = table_rows[pos]
            row_data        = row.find_elements(By.XPATH, './td')
            row_date        = row_data[2]
            row_date_text   = row_data[2].text
            row_vendor_name = row_data[3].text
         
            if pos not in completed_orders:
                
                row_date.click()
                WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.TAG_NAME, 'table')))

                items = self._scrape_order()

                self._save_order_as_excel(items, f'{SAVE_FILE_PATH}{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.xlsx')
                
                time.sleep(2)

                if download_pdf:
                    
                    self._download_order_pdf()
                    time.sleep(3)
                    self._rename_new_order_file(DOWNLOAD_PATH, f'{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.pdf')

                completed_orders.append(pos)
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
                
                completed_orders.append(pos)


                time.sleep(2)


                self.driver.back()
                time.sleep(3)

    '''
    '''
    def get_order_from_vendor(self, store: str, vendor: str, download_pdf=False) -> None:
        # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        
        # Iterate through the table rows. If the vendor isn't found, try to scoll to bottom of page. If vendor still isn't found, return None.
        vendor_found = False
        vendor_not_in_list = False
        counter = 0
        while not vendor_found and not vendor_not_in_list:
       
            table_body = self.driver.find_element(By.XPATH, './/tbody')
            table_rows = table_body.find_elements(By.XPATH, './tr')
            for pos, row in enumerate(table_rows):
            
                table_body      = self.driver.find_element(By.XPATH, './/tbody')
                table_rows      = table_body.find_elements(By.XPATH, './tr')
                row             = table_rows[pos]
                row_data        = row.find_elements(By.XPATH, './td')
                row_date        = row_data[2]
                row_date_text   = row_data[2].text
                row_vendor_name = row_data[3].text
          
                if pos == (len(table_rows) - 1) and row_vendor_name != vendor:
              
                    elem = self.driver.find_element(By.TAG_NAME, "html")
             
                    elem.send_keys(Keys.END)
                    continue

                if row_vendor_name == vendor:
                    vendor_found = True
                    row_date.click()
                    WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.TAG_NAME, 'table')))

                    items = self._scrape_order()

                    self._save_order_as_excel(items, f'{ORDER_FILES_PATH}{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.xlsx')
                    
                    time.sleep(2)

                    if download_pdf:
                        
                        self._download_order_pdf()
                        time.sleep(3)
                        self._rename_new_order_file(DOWNLOAD_PATH, f'{row_vendor_name} _ {store} {row_date_text.replace("/", "")}.pdf')
                    
                    self.driver.back()
                    time.sleep(3)
              
            
            if counter == 1:
                vendor_not_in_list = True

            counter +=1
        return

    def delete_order(self, store: str, vendor: str) -> None:
        pass

    def delete_all_orders(self, store: str) -> None:
        # Go to the orders page
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(6)

        
        table_body = self.driver.find_element(By.XPATH, './/tbody')
        table_rows = table_body.find_elements(By.XPATH, './tr')

        order_counter = len(table_rows)
        while order_counter > 0:
            table_body      = self.driver.find_element(By.XPATH, './/tbody')
            table_rows      = table_body.find_elements(By.XPATH, './tr')
            row             = table_rows[order_counter-1]
            row_data        = row.find_elements(By.XPATH, './td')
            row_date        = row_data[2]
            row_date_text   = row_data[2].text
            row_vendor_name = row_data[3].text

            row_date.click()
        
            try:
                WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div[2]/div/div[3]/div/div[2]/span[1]/a')))
            except:
                #ActionChains(self.driver).scroll_to_element(iframe).perform()
                js_code = 'arguments[0].scrollIntoView();'
                self.driver.execute_script(js_code, self.driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div[2]/div/div[3]/div/div[2]/span[1]/a'))

            delete_button = self.driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div[2]/div/div[3]/div/div[2]/span[1]/a')
            delete_button.click()
            
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'confirmOrderDeleteModal')))
            confirm_delete_modal = self.driver.find_element(By.ID, 'confirmOrderDeleteModal')
            modal_footer = confirm_delete_modal.find_element(By.CLASS_NAME, 'modal-footer')
            footer_buttons = modal_footer.find_elements(By.TAG_NAME, 'button')
            delete_button = footer_buttons[1]
            delete_button.click()
            order_counter -= 1
            time.sleep(4)

        return

    def input_transfer(self, transfer: Transfer) -> None:
        
        
        if not self.is_logged_in: self.login()

        time.sleep(3)

        self.driver.get('https://app.craftable.com/buyer/2/14376/transfers/list')

        time.sleep(5)

        new_transfer_button = self.driver.find_element(By.XPATH, '//a[text()="New Transfer"]')
        new_transfer_button.click()

        time.sleep(4)

        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        date_input = transfer_form_inputs[0].find_element(By.XPATH, './/input')
        toggle_out = transfer_form_inputs[1].find_element(By.XPATH, './/input') # We can do this because we only want the first input.
        
        date_input.click()
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flatpickr-calendar')))
        date_input_current_month = self.driver.find_element(By.CLASS_NAME, 'cur-month')
        
        # NEED TO UPDATE SO IT CAN CHOOSE THE CORRECT MONTH!!!!!

        calendar = self.driver.find_element(By.CLASS_NAME, 'dayContainer')
    

        today = calendar.find_element(By.XPATH, f'.//span[@class="flatpickr-day "][text()="{transfer.date.day}"]')
        today.click()
        time.sleep(2)
        toggle_out.click()
        time.sleep(2)

        '''Have to search these again to avoid stale references...'''
        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        store_to_select = transfer_form_inputs[2].find_element(By.XPATH, './/div[@class="search ember-view input-select-searchable"]')
        store_to_select.click()

        time.sleep(2)

        options = self.driver.find_elements(By.XPATH, './/li[@class="select2-results__option"]')
        for option in options:
            choice_id_full = option.get_attribute('data-select2-id')
            choice_id = choice_id_full.split('-')[-1]
            if choice_id == self.stores[transfer.store_to]:
                choice = self.driver.find_element(By.XPATH, f'//li[@data-select2-id="{choice_id_full}"]')
                choice.click()
                break

        time.sleep(4)

        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')
        transfer_modal_footer = transfer_modal.find_element(By.XPATH, './/div[@class="modal-footer "]')
        submit_button = transfer_modal_footer.find_elements(By.TAG_NAME, 'button')[1]

        submit_button.click()

        time.sleep(4)

        for item in transfer.items:

            # Click the add-item button
            page_body = self.driver.find_element(By.XPATH, './/div[@class="card-body"]')
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div[2]/div/div/div[3]/div[1]/span/a')))
            add_item_button = page_body.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div[2]/div/div/div[3]/div[1]/span/a')
            
            add_item_button.click()

            time.sleep(4)

            # Enter the item name
            item_input = self.driver.find_element(By.ID, 'typeahead')
            item_input.send_keys(item.name)
            time.sleep(4)

            # Select the item from the dropdown
            item_choice_container = self.driver.find_element(By.XPATH, './/div[@class="input-group input-typeahead-container input-group-merge"]')
            item_choice = item_choice_container.find_elements(By.XPATH, './following-sibling::div/div[@class="input-type-ahead "]/div[@class="input-type-ahead-row"]')[0]
            item_choice.click()
            

            transfer_modal = self.driver.find_element(By.ID, 'transferItemModal')
            transfer_form = transfer_modal.find_element(By.XPATH, './/form')
            quantity_input_container = transfer_form.find_elements(By.XPATH, './div')[2]
            quantity_input = quantity_input_container.find_element(By.XPATH, './/input')
            quantity_input.send_keys(Keys.BACKSPACE)
            quantity_input.send_keys(item.quantity)

            time.sleep(2)

            add_transfer_item_button = self.driver.find_element(By.XPATH, './/button[text()="Add Transfer Line"]')
            add_transfer_item_button.click()

            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, './/div[@class="_c-notification__content"][text()="Successfully added a Transfer Line"]')))
            
            # time.sleep(5)
        
        submit_transfer_button = self.driver.find_element(By.XPATH, './/a[text()="Request"]')
        return

    def _rename_new_order_file(self, path:str, file_name:str) -> None:
     
        rename(f'{path}Order.pdf', f'{ORDER_FILES_PATH}{file_name}')
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
    
    '''
    Assumes the current driver is 'looking at' an order page.

    Scrapes the current page for order data and returns the data 
    as a 2-D list.
    '''
    def _scrape_order(self) -> list:
        order_table = self.driver.find_element(By.TAG_NAME, 'tbody')
        item_rows   = order_table.find_elements(By.TAG_NAME, 'tr')

        items = []
        for item in item_rows:
            item_info = item.find_elements(By.TAG_NAME, 'td')
        
            item_sku   = item_info[2].text
            item_name  = item_info[3].find_element(By.XPATH, './/a').text
            quantity   = item_info[5].text
            cost_per   = item_info[6].text
            total_cost = item_info[7].text

            items.append([
                item_sku, 
                item_name, 
                quantity, 
                cost_per, 
                total_cost
                ])
            
        return items
    
    '''
    Assumes the current driver is 'looking at' an order page.

    Clicks the download button on the order page.
    '''
    def _download_order_pdf(self) -> None:
        download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
        ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
        return
    
    '''
    Takes in a 2-D list of item data assuming the following 
    column formatting:

    SKU | Item Name | Quantity | Cost Per | Total Cost

    Saves to an Excel file with the supplied file name/path.
    '''
    def _save_order_as_excel(self, item_data, file_name) -> None:
        workbook = Workbook()
        sheet = workbook.active
        
        col_headers = ['SKU', 'Item', 'Quantity', 'Cost Per', 'Total Cost']
        # Insert headers
        for pos, header in enumerate(col_headers):
            sheet.cell(row=1, column=pos+1).value = header

        # Insert item data
        for pos, item in enumerate(item_data):
            for info_pos, item_info in enumerate(item):
                sheet.cell(row=pos+2, column=info_pos+1).value = item_info
        
        workbook.save(file_name)
        return
    
    def _delete_order_protocol(self) -> None:
        pass