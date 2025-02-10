from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
import time
from pynput.keyboard import Key, Controller
from os import rename, getenv, scandir
import os
from os.path import join
from pprint import pprint
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.webdriver import WebDriver
from dotenv import load_dotenv

from openpyxl import Workbook, load_workbook

from backend.transferring import Transfer
from ..orders.OrderManager import OrderManager
from ..orders.Order import Order

from datetime import datetime

from pathlib import Path

# PRICING_FILES_PATH  = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\pricing\\VendorSheets\\'
# DOWNLOAD_PATH       = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\downloads\\'

'''
Craftable Bot utlizes Selenium to interact with the Craftable website. 
'''
class CraftableBot:

    def __init__(self, driver: WebDriver, username: str, password: str, order_manager: OrderManager = None):
        self.driver        = driver
        self.username      = username
        self.password      = password
        self.order_manager = order_manager or OrderManager()

        self.is_logged_in = False
        self.stores = {
            'BAKERY':      '14376',
            'DOWNTOWN':    '14373',
            'EASTHILL':    '14374',
            'TRIPHAMMER':  '14375',
            'COLLEGETOWN': '14372',
        }

        self.site_map = {
            'login_page': 'https://app.craftable.com/signin'
        }

    def __enter__(self):
        self.login()
        return self
    
    def __exit__(self, type, value, traceback):
        # print(value)
        try:
            self.close_session()
        except OSError as os_error:
            # print(os_error)
            pass
        time.sleep(2) # We need to avoid a race condition when the session closes right before the script ends.
        return True
    
    '''
    Login to the Craftable website using the standard landing page.

    This method assumes the bot knows the username and password.

    Args:
        None

    Returns:
        None
    '''
    def login(self) -> None:

        self.driver.get(self.site_map['login_page'])

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
        print('\nClosing session...', flush=True)
        try:
            self.driver.close()
        except:
            print('...session failed to close.', flush=True)

        print('...success.', flush=True)
        return
    
    '''
    Switch to another store's page.

    Args:
        store_code: store name

    Returns:
        None
    '''
    def switch_store(self, store: str) -> None:

        if store not in self.stores: return

        if store == 'DIRECTOR':
            self.driver.get('https://app.craftable.com/director/2/583')
            return
        
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}')

        #WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.CLASS_NAME, 'row home-cards-orders-invoices')))
        time.sleep(5)
        return

    def go_to_store_order_page(self, store: str) -> None:
        self.driver.get(f'https://app.craftable.com/buyer/2/{self.stores[store]}/orders/list')
        time.sleep(5)
        return
    
    ''' Download orders from Craftable.

    ARGS

    stores: a list of stores for which to retrieve orders.
    vendors: a list of vendors to retrieve orders of. If none supplied, then all possible orders are retrieved.
    download_pdf: a boolean of whether to download an accompanying PDF file.
    update: a boolean of whether to overwrite currently saved order data.

    RETURN

    None

    Will scrape the Craftable order page for each store and selected vendors, download and generate the appropriate
    files, and save in the ORDER_FILES_PATH.

    '''
    def download_orders(self, stores: list, vendors=list, download_pdf=True, update=True) -> None:

        print('\nBeginning to download orders from Craftable.', flush=True)
        for store in stores:
            
            print(f'\nGetting order page for {store}.', flush=True)
            self.go_to_store_order_page(store)
            time.sleep(6)

            table_body = self.driver.find_element(By.XPATH, './/tbody')
            table_rows = table_body.find_elements(By.XPATH, './tr')

            print('Orders found.', flush=True)
            completed_orders = [] # Store the index of the rows here
            for pos, row in enumerate(table_rows):
                table_body      = self.driver.find_element(By.XPATH, './/tbody')
                table_rows      = table_body.find_elements(By.XPATH, './tr')
                row             = table_rows[pos]
                row_data        = row.find_elements(By.XPATH, './td')
                row_date        = row_data[2]
                row_date_text   = row_data[2].text
                row_vendor_name = row_data[3].text
                
              
                row_date_formatted = self._convert_date_format(row_date_text, '%m/%d/%Y', '%Y%m%d')
                
                if pos in completed_orders:
                    continue

                # If vendors have been supplied and the current vendor isn't in the list, we skip it.
                if (vendors) and (row_vendor_name not in vendors):
                    print(f'{row_vendor_name} not wanted...skipping.')
                    completed_orders.append(pos) # Is this superfluous?
                    continue
    
                print(f'\nRetrieving order for {row_vendor_name}.', flush=True)
                row_date.click()
                WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.TAG_NAME, 'table')))
                
                # print('Scraping order.', flush=True)
                items = self._scrape_order()

                print('Checking if update is necessary.', flush=True)
                if update and self._update_existing_order(store, row_vendor_name, row_date_formatted, items):
                    print('No update necessary, continuing to next order.', flush=True)
                    completed_orders.append(pos)
                    self.driver.back()
                    time.sleep(2)
                    continue
                        
                self._save_order_as_excel(items, store=store, vendor=row_vendor_name, date=row_date_formatted )
                time.sleep(1)

                if download_pdf:
                    self._download_order_pdf()
                    time.sleep(3)
                    self._rename_new_order_file(store=store, vendor=row_vendor_name, date=row_date_formatted)

                completed_orders.append(pos)
                self.driver.back()
                time.sleep(3)

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
        print(order_counter, flush=True)
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
                WebDriverWait(self.driver, 35).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-danger')))
            except:
                # #ActionChains(self.driver).scroll_to_element(iframe).perform()
                # js_code = 'arguments[0].scrollIntoView();'
                # self.driver.execute_script(js_code, self.driver.find_element(By.XPATH, 'btn-danger'))
                pass
              

            tries = 2
            while tries >= 0:
                try:
                    delete_button = self.driver.find_element(By.CLASS_NAME, 'btn-danger')
                    delete_button.click()
                    break
                except:
                    tries -= 1
            
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'confirmOrderDeleteModal')))
            confirm_delete_modal = self.driver.find_element(By.ID, 'confirmOrderDeleteModal')
            modal_footer = confirm_delete_modal.find_element(By.CLASS_NAME, 'modal-footer')
            footer_buttons = modal_footer.find_elements(By.TAG_NAME, 'button')
            delete_button = footer_buttons[1]
            delete_button.click()
            order_counter -= 1
            time.sleep(5)

        return

    def input_transfer(self, transfer: Transfer) -> None:
        
        
        if not self.is_logged_in: self.login()

        time.sleep(3)

        self.driver.get('https://app.craftable.com/buyer/2/14376/transfers/list')

        time.sleep(5)

        print('\nCreating new transfer in Craftable...', flush=True)
        new_transfer_button = self.driver.find_element(By.XPATH, '//a[text()="New Transfer"]')
        new_transfer_button.click()

        time.sleep(4)

        print('Entering transfer information...', flush=True)
        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        date_input = transfer_form_inputs[0].find_element(By.XPATH, './/input')
        toggle_out = transfer_form_inputs[1].find_element(By.XPATH, './/input') # We can do this because we only want the first input.
        
        print('...transfer date...', flush=True)
        date_input.click()
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flatpickr-calendar')))
        date_input_current_month = self.driver.find_element(By.CLASS_NAME, 'cur-month')
        
        # NEED TO UPDATE SO IT CAN CHOOSE THE CORRECT MONTH!!!!!

        calendar = self.driver.find_element(By.CLASS_NAME, 'dayContainer')
        print(transfer.date.day)
        today = calendar.find_element(By.XPATH, f'.//span[@class="flatpickr-day "][text()="{transfer.date.day}"]')
        print('done')
        today.click()
        
        print('...outbound transfer.', flush=True)
        time.sleep(2)
        toggle_out.click()
        time.sleep(2)

        '''Have to search these again to avoid stale references...'''
        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        print('...transfer destination.', flush=True)
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
        WebDriverWait(self.driver, 120).until(EC.element_to_be_clickable((By.ID, 'transferNewModal')))
        transfer_modal        = self.driver.find_element(By.ID, 'transferNewModal')
        transfer_modal_footer = transfer_modal.find_element(By.XPATH, './/div[@class="modal-footer "]')

        print('...submitting.', flush=True)
        submit_button         = transfer_modal_footer.find_elements(By.TAG_NAME, 'button')[1]

        submit_button.click()

        time.sleep(4)

        print('Beginning to enter transfer items...', flush=True)
        for item in transfer.items:
            
            # Click the add-item button
            page_body = self.driver.find_element(By.XPATH, './/div[@class="card-body"]')
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Add Transfer Line"]')))
            add_item_button = page_body.find_element(By.XPATH, '//a[text()="Add Transfer Line"]')
            add_item_button.click()

            time.sleep(2)

            # Enter the item name
            try:

               
                item_input = self.driver.find_element(By.ID, 'typeahead')
                item_input.send_keys(item.name)
                time.sleep(5)

                # Select the item from the dropdown
                item_choice_container = self.driver.find_element(By.XPATH, './/div[@class="input-group input-typeahead-container input-group-merge"]')
                item_choice = item_choice_container.find_elements(By.XPATH, './following-sibling::div/div[@class="input-type-ahead "]/div[@class="input-type-ahead-row"]')[0]
                item_choice.click()
                
                


                transfer_modal           = self.driver.find_element(By.ID, 'transferItemModal')
                transfer_form            = transfer_modal.find_element(By.XPATH, './/form')
                quantity_input_container = transfer_form.find_elements(By.XPATH, './div')[2]
                quantity_input           = quantity_input_container.find_element(By.XPATH, './/input')
                quantity_input.send_keys(Keys.BACKSPACE)
                quantity_input.send_keys(item.quantity)

                time.sleep(3)

                for i in range(3):
                    try:
                        add_transfer_item_button = self.driver.find_element(By.XPATH, './/button[text()="Add Transfer Line"]')
                        add_transfer_item_button.click()
                        WebDriverWait(self.driver, 180).until(EC.element_to_be_clickable((By.XPATH, './/div[@class="_c-notification__content"][text()="Successfully added a Transfer Line"]')))
                        break
                    except:
                        pass
                    
            except:
                transfer_modal = self.driver.find_element(By.ID, 'transferItemModal')
                close_button = transfer_modal.find_element(By.CLASS_NAME, 'close')
                close_button.click()
                print(item.name, transfer.store_to, flush=True)
                time.sleep(4)
                continue
            # time.sleep(5)
        
        submit_transfer_button = self.driver.find_element(By.XPATH, './/a[text()="Request"]')
        return
        
    def _rename_new_order_file(self, store: str, vendor: str, date: str) -> None:

        original_file = self.order_manager.get_downloads_directory() / 'Order.pdf'

        if not original_file.exists():
            print(f'Warning: Expected file not found: {original_file}')
            return
        
        new_filename = self.order_manager.generate_filename(store=store, vendor=vendor, date=date, file_extension='.pdf')
        new_filepath = self.order_manager.get_order_files_directory() / new_filename
        
        original_file.rename(new_filepath)
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
    
    def _save_order_as_excel(self, item_data, store: str, vendor: str, date: str) -> None:

        print('Saving order as an Excel workbook.', flush=True)

        order = Order(store, vendor, date, items=item_data)
     
        order_as_workbook = order.to_excel_workbook()

        new_filename = self.order_manager.generate_filename(store=store, vendor=vendor, date=date, file_extension='.xlsx')
        new_filepath = self.order_manager.get_order_files_directory() / new_filename

        order_as_workbook.save(new_filepath)
        order_as_workbook.close()

        return
    
    def _delete_order_protocol(self) -> None:
        pass

    def _convert_date_format(self, date_str: str, input_format: str, output_format: str) -> str:
        """
        Converts a date string from one format to another.

        Args:
            date_str (str): The date string to be converted.
            input_format (str): The format of the input date string (e.g., "%m/%d/%Y").
            output_format (str): The desired output format (e.g., "%Y%m%d").

        Returns:
            str: The converted date string, or an error message if invalid.
        """
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return f"Invalid date format: {date_str}. Expected format: {input_format}"
        
    def _extract_order_table_rows(self, row) -> tuple:
        pass

    def _update_existing_order(self, store, vendor_name, date_formatted, items) -> bool:

        """Handles the update protocol for checking existing orders and removing outdated files."""
        print('\nBeginning order update protocol.', flush=True)

        preexisting_workbook_filename = self.order_manager.generate_filename(
            store=store, 
            vendor=vendor_name, 
            date=date_formatted, 
            file_extension='.xlsx'
        )
        
        print('Checking for pre-existing order data.', flush=True)
        preexisting_workbook_path = self.order_manager.get_order_files_directory() / vendor_name / preexisting_workbook_filename
        preexisting_file_exists = preexisting_workbook_path.exists()
        
        if not self.order_manager.get_vendor_orders_directory(vendor_name): 
            print('No file to update, continuing with data download.', flush=True)
            return False
        if not preexisting_file_exists: 
            print('No file to update, continuing with data download.', flush=True)
            return False
        
        print('Extracting saved data...', flush=True)
        workbook = load_workbook(preexisting_workbook_path, read_only=True)
        sheet = workbook.active
        saved_items = [[cell.value for cell in row] for row in sheet.iter_rows(min_row=2)]
        workbook.close()

        print('Comparing new data with pre-existing data.', flush=True)
        if set(map(tuple, items)) == set(map(tuple, saved_items)):
            print('New data matches old data, skipping update protocol.', flush=True)
            return True  # Skip further processing

        self._remove_old_files(preexisting_workbook_path)

        return False  # Continue with saving new data
    
    def _remove_old_files(self, workbook_path):
        """Removes outdated XLSX and PDF files."""
        try:
            print('Removing out-of-date files.', flush=True)

            if os.path.isfile(workbook_path):
                print(f'Removing file: {workbook_path}')
                os.remove(workbook_path)

            pdf_path = workbook_path.with_suffix('.pdf')
            if os.path.isfile(pdf_path):
                print(f'Removing file: {pdf_path}')
                os.remove(pdf_path)

        except OSError as e:
            print(f'Error removing files: {e}')
            if e.errno == 13:
                print('File is being accessed by another program at time of deletion. Aborting file replacement.')
