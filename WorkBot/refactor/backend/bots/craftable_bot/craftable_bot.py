from datetime import datetime
from pathlib import Path
import os
import time

from config.paths import DOWNLOADS_PATH

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.webdriver import WebDriver

from pynput.keyboard import Key, Controller
from openpyxl import Workbook, load_workbook

from backend.models.item import Item 
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.transfer import Transfer

from backend.coordinators.order_coordinator import OrderCoordinator
from backend.coordinators.transfer_coordinator import TransferCoordinator

from backend.utils.logger import Logger
from backend.utils.helpers import convert_date_format, string_to_datetime

from backend.bots.bot_mixins import SeleniumBotMixin
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException



def temporary_login(func):
    def wrapper(self, *args, **kwargs):
        self.login()
        try:
            return func(self, *args, **kwargs)
        finally:
            self.close_session()
    return wrapper


def login_necessary(func):
    def wrapper(self, *args, **kwargs):
        if not self.is_logged_in:
            self.login()
        return func(self, *args, **kwargs)
    return wrapper

'''
Craftable Bot utlizes Selenium to interact with the Craftable website. 
'''
@Logger.attach_logger
class CraftableBot(SeleniumBotMixin):

# region ---- Global Class Variables --------------------

    site_map = {
            'login_page': 'https://app.craftable.com/signin',
            'orders_page': 'https://app.craftable.com/buyer/2/{store_id}/orders/list',
            'transfer_page': 'https://app.craftable.com/buyer/2/{store_id}/transfers/list',
            'audit_page': 'https://app.craftable.com/director/2/583/audits/history/list'
    }
    
    stores = {
            'BAKERY':      '14376',
            'DOWNTOWN':    '14373',
            'EASTHILL':    '14374',
            'TRIPHAMMER':  '14375',
            'COLLEGETOWN': '14372',
            'Bakery':      '14376',
            'Downtown':    '14373',
            'Easthill':    '14374',
            'Triphammer':  '14375',
            'Collegetown': '14372',
            'Director': '583',
            'DIRECTOR': '583',
    }
    
# endregion

    def __init__(self, username: str, password: str, 
                 order_coordinator: OrderCoordinator = None, 
                 transfer_coordinator: TransferCoordinator = None):
        
        
        super().__init__(DOWNLOADS_PATH, username=username, password=password)

        self.order_coordinator    = order_coordinator or OrderCoordinator()
        self.transfer_coordinator = transfer_coordinator or TransferCoordinator()

        self.is_logged_in = False
        
# region ---- Legacy Code -------------------------------
    # def __enter__(self):
    #     self.logger.info('Starting CraftableBot session.')
    #     self.login()
    #     return self
    
    # def __exit__(self, type, value, traceback):
    #     self.logger.info('Ending CraftableBot session.')
    #     try:
    #         self.close_session()
    #     except Exception as e:
    #         self.logger.warning(f'Issue with closing session: {e}')

    #     time.sleep(2) # Prevents race condition with OS program manager
    #     return True
# endregion

    # @Logger.log_exceptions
    # @property
    # def fresh_command(self):
    #     # syntactic sugar: @self.fresh_command
    #     return self.fresh
    
# region ---- Session Page Control ----------------------
    
    '''
    Login to the Craftable website using the standard landing page.

    This method assumes the bot knows the username and password.

    Args:
        None

    Returns:
        None
    '''
    @Logger.log_exceptions
    def login(self) -> None:
        self.logger.info('Logging into Craftable.')
        self.driver.get(self.site_map['login_page'])

        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, './/form')))
        
        login_form = self.driver.find_element(By.XPATH, './/form')
        
        fieldsets         = login_form.find_elements(By.XPATH, './/fieldset')
        email_fieldset    = fieldsets[0]
        password_fieldset = fieldsets[1]

        email_input    = email_fieldset.find_element(By.XPATH, './/input')
        password_input = password_fieldset.find_element(By.XPATH, './/input')

        submit_button_div = login_form.find_elements(By.XPATH, './/button')[0]
        
        email_input.send_keys(self.username)
        password_input.send_keys(self.password)

        submit_button_div.click()
        time.sleep(5)

        self.is_logged_in = True

        self.logger.info('Login successful.')
        return
    
    '''
    Close the driver session.

    Args:
        None

    Returns:
        None
    '''
    def close_session(self) -> None:
        self.logger.info('Closing WebDriver session.')

        try: 
            self.driver.close()
        except Exception as e: 
            self.logger.error(f'Error closing WebDriver session: {e}')

        self.logger.info('WebDriver session closed.')
        return
    
    '''
    Switch to another store's page.

    Args:
        store_code: store name

    Returns:
        None
    '''
    @Logger.log_exceptions
    def switch_store(self, store: str) -> None:
        
        store = store.upper()

        if store not in self.stores: 
            self.logger.warning(f'Invalid store name: {store}.')
            return

        if store == 'DIRECTOR':
            self.driver.get('https://app.craftable.com/director/2/583')
            return
        
        self.logger.info(f'Switching to store: {store}.')
        store_url = f'https://app.craftable.com/buyer/2/{self.stores[store]}'
        self.driver.get(store_url)

        #WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.CLASS_NAME, 'row home-cards-orders-invoices')))
        time.sleep(5)
        return

    @classmethod
    @Logger.log_exceptions
    def get_url(cls, key: str, store: str = None) -> str:

        cls.logger.debug('Retrieving URL from site map.')

        if key not in cls.site_map:
            cls.logger.error(f'Invalid site map key: {key}')
            return ''
        
        if '{store_id}' in cls.site_map[key]:
            if store not in cls.stores:
                cls.logger.error(f'Invalid store name: {store}')
                return ''
            return cls.site_map[key].format(store_id=cls.stores[store])
        
        return cls.site_map[key]
   
# endregion 

# region ---- Order Downloading -------------------------
    
    ''' Download orders from Craftable.

    ARGS

    stores:       a list of stores for which to retrieve orders.
    vendors:      a list of vendors to retrieve orders of. If none supplied, then all possible orders are retrieved.
    download_pdf: a boolean of whether to download an accompanying PDF file.
    update:       a boolean of whether to overwrite currently saved order data.

    RETURN

    None

    Will scrape the Craftable order page for each store and selected vendors, download and generate the appropriate
    files, and save in the ORDER_FILES_PATH.

    i. Assumes the bot is currrently logged in.

    '''

    @SeleniumBotMixin.with_session(login=True)
    @Logger.log_exceptions
    def download_orders(self, stores: list, vendors=list, download_pdf=True, update=True) -> None:
       
        self.logger.info('Starting order download protocol.')
        for store in stores:
            
            self.logger.info(f'Accessing order page for {store}.')
            store_order_url = self.get_url('orders_page', store=store)
            self.driver.get(store_order_url)
            time.sleep(6)
            
            table_rows = self._get_order_table_rows()
            if not table_rows:
                self.logger.info(f'No more orders found for {store}. Moving to next store.')
                break 

            for pos in range(len(table_rows)):
                stale_reference_table_rows = self._get_order_table_rows() # Refresh to avoid stale references
                self._process_order_row(store, stale_reference_table_rows[pos], vendors, download_pdf, update)

        self.logger.info('Order download complete.')
        self.logger.info('Closing WebDriver session.')
        self.end_session

        return
   
    def _get_order_table_rows(self) -> list:
        '''Returns all order rows in the table, handling stale references.'''
        try:
            table_body = self.driver.find_element(By.XPATH, './/tbody')
            return table_body.find_elements(By.XPATH, './tr')
        except Exception as e:
            self.logger.warning(f'Failed to retrieve order table: {e}')
            return []
    
    def _process_order_row(self, store: str, row, vendors: list, download_pdf: bool, update: bool) -> None:
        '''Processes a single order row: extracts data, downloads order, and saves it.'''

        row_data = row.find_elements(By.XPATH, './td')
        row_date_text = row_data[2].text
        row_vendor_name = row_data[3].text
        row_date_formatted = convert_date_format(row_date_text, '%m/%d/%Y', '%Y%m%d')

        if vendors and row_vendor_name not in vendors:
            self.logger.debug(f'Skipping vendor {row_vendor_name}.')
            return 

        self.logger.info(f'Retrieving order for {row_vendor_name} ({row_date_text}).')

        row_data[2].click()
        
        WebDriverWait(self.driver, 45).until(EC.element_to_be_clickable((By.TAG_NAME, 'table')))
        items = self._scrape_order()

        order_to_check_update = Order(store=store, vendor=row_vendor_name, date=row_date_formatted, items=items)
        if update and self._update_existing_order(order_to_check_update):
            self.logger.info(f'Order for {row_vendor_name} is up-to-date. Skipping.')
            self.driver.back()
            time.sleep(2)
            return 

        self.logger.info(f'Saving order for {row_vendor_name}.')
        order_to_save = Order(store=store, vendor=row_vendor_name, date=row_date_formatted, items=items)
        self.order_coordinator.save_order_file(order_to_save)
        self.order_coordinator.save_order_to_db(order_to_save)
        # self.order_manager.save_order(order_to_save)
        # self.order_manager.upload_order_to_api(order_to_save)

        time.sleep(1)


        if download_pdf:
            self.order_coordinator.expect_downloaded_pdf(order_to_save)
            self._download_order_pdf()

        self.driver.back()
        time.sleep(3)
        return 

    def _find_order_row(self, table_rows, vendor_name, date_text):
        '''Finds the correct order row by vendor name and order date.'''
        for row in table_rows:
            row_data = row.find_elements(By.XPATH, './td')
            if len(row_data) < 4:
                continue  # Skip malformed rows
            if row_data[2].text == date_text and row_data[3].text == vendor_name:
                return row
        return None
    

# endregion
   
# region ---- Order Deletion ----------------------------
    @SeleniumBotMixin.with_session(login=True)
    @Logger.log_exceptions
    def delete_orders(self, stores: list[str], vendors: list[str] = None) -> None:

        for store in stores:
            self.logger.info(f'Starting order deletion for store: {store}.')
            
            # if store not in stores:
            #     self.logger.warning(f'Invalid store name: {store}, Skipping.')
            #     continue

            store_orders_url = self.get_url('orders_page', store=store)
            print(store_orders_url)
            self.logger.debug(f'Navigating to: {store_orders_url}')
            self.driver.get(store_orders_url)
            time.sleep(6)

            table_body = self.driver.find_elements(By.XPATH, './/tbody')
            if not table_body:
                self.logger.info(f'No orders found for store: {store}. Skipping.')
                continue
            table_rows = table_body[0].find_elements(By.XPATH, './tr')

            self.logger.info(f'Found {len(table_rows)} orders for deletion.')

            while table_rows:
                row             = table_rows[-1]  # Always delete the last order first
                row_data        = row.find_elements(By.XPATH, './td')
                row_date_text   = row_data[2].text
                row_vendor_name = row_data[3].text

                # If vendors list is provided, only delete matching vendor orders
                if vendors and row_vendor_name not in vendors:
                    self.logger.debug(f'Skipping order from vendor: {row_vendor_name}.')
                    table_rows.pop()
                    continue

                self.logger.info(f'Deleting order: {row_vendor_name} ({row_date_text})')
                self._delete_order(row)
                
                # self.driver.back()
                # time.sleep(5)
                # Refresh table after deletion
                try:
                    table_body = self.driver.find_element(By.XPATH, './/tbody')
                    table_rows = table_body.find_elements(By.XPATH, './tr')
                except:
                    self.logger.info('No orders table found. All orders deleted.')
                    break

            self.logger.info(f'Finished deleting orders for store: {store}.')

    def _delete_order(self, row) -> None:
        '''Handles the deletion of a single order.'''
        try:
            row.find_elements(By.XPATH, './td')[2].click()
            WebDriverWait(self.driver, 35).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-danger')))
        except Exception as e:
            self.logger.warning(f'Could not open order details: {e}')
            return

        self._click_delete_button()
        self._confirm_delete()

    def _click_delete_button(self) -> None:
        '''Clicks the delete button within the order page.'''
        for attempt in range(3):
            try:
                delete_button = self.driver.find_element(By.CLASS_NAME, 'btn-danger')
                delete_button.click()
                self.logger.debug('Delete button clicked.')
                return
            except Exception as e:
                self.logger.warning(f'Attempt {attempt+1} failed to click delete button: {e}')
                time.sleep(2)

        self.logger.error('Failed to click delete button after 3 attempts.')

    def _confirm_delete(self) -> None:
        '''Handles confirming the deletion of an order.'''
        try:
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'confirmOrderDeleteModal')))
            confirm_modal = self.driver.find_element(By.ID, 'confirmOrderDeleteModal')
            modal_footer  = confirm_modal.find_element(By.CLASS_NAME, 'modal-footer')
            delete_button = modal_footer.find_elements(By.TAG_NAME, 'button')[1]

            delete_button.click()
            self.logger.info('Order deletion confirmed.')
            time.sleep(5)
        except Exception as e:
            self.logger.error(f'Failed to confirm deletion: {e}')


   # endregion

# region ---- Order Transfers ---------------------------
    @SeleniumBotMixin.with_session(login=True)
    @Logger.log_exceptions
    def input_transfers(self, transfers: list) -> None:

        self.logger.info(f'Starting protocol for {len(transfers)} transfers.')
        for transfer in transfers:
            self.input_transfer(transfer)
        self.logger.info('Transfers complete.')
        return
    
    @Logger.log_exceptions
    def input_transfer(self, transfer: Transfer) -> None:
        
            
        self.logger.info(f'Starting transfer protocol for {len(transfer.transfer_items)} items from {transfer.origin} to {transfer.destination} on {transfer.transfer_date}')
        if not self.is_logged_in: self.login()

        time.sleep(3)

        transfer_url = self.get_url('transfer_page', store=transfer.origin)
        self.driver.get(transfer_url)

        time.sleep(5)

        self._start_new_transfer()
        self._enter_transfer_details(transfer)
        self._submit_transfer()
        self._input_transfer_items(transfer)

        self.logger.info(f'Transfer for {len(transfer.transfer_items)} items from {transfer.origin} to {transfer.destination} on {transfer.transfer_date} completed successfully.')
        # NEED TO MOVE THE COMPLETED TRANSFER FILE TO THE 'COMPLETED' DIRECTORY
        # submit_transfer_button = self.driver.find_element(By.XPATH, './/a[text()='Request']')
        return

    def _start_new_transfer(self) -> None:
        self.logger.info('Creating new transfer in Craftable.')
        new_transfer_button = self.driver.find_element(By.XPATH, '//a[text()="New Transfer"]')
        new_transfer_button.click()

        time.sleep(4) # WebDriver wait and exception handling...or we just wait and pray.

        return
    
    def _enter_transfer_details(self, transfer: Transfer) -> None:

        self.logger.info(f'Entering transfer details: {transfer.origin} to {transfer.destination} on {transfer.transfer_date}')

        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        date_input = transfer_form_inputs[0].find_element(By.XPATH, './/input')
        toggle_out = transfer_form_inputs[1].find_element(By.XPATH, './/input') # We can do this because we only want the first input.
        
        self.logger.info('Opening transfer date calendar.')
        date_input.click()
        
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flatpickr-calendar')))
        # date_input_current_month = self.driver.find_element(By.CLASS_NAME, 'cur-month')
        
        # calendar_current_month = self.driver.find_element(By.CLASS_NAME, 'cur-month')
        # calendar_current_year_input = self.driver.find_element(By.CLASS_NAME, 'cur_year')

        # calendar_current_year_input.send_keys('2025')

        # NEED TO UPDATE SO IT CAN CHOOSE THE CORRECT MONTH!!!!!
        self.logger.info(f'Selecting calendar date: {transfer.transfer_date}')
        transfer_date_obj = datetime.strptime(transfer.transfer_date, '%Y-%m-%d') 

        self._change_calendar_date(transfer_date_obj)

        # calendar = self.driver.find_element(By.CLASS_NAME, 'dayContainer')
        # print(transfer.date.day)
        # today = calendar.find_element(By.XPATH, f'.//span[@class='flatpickr-day '][text()='{transfer.date.day}']')
        # today.click()
        
        self.logger.info('Marking transfer as "Out".')
        time.sleep(2)
        toggle_out.click()
        time.sleep(2)

        '''Have to search these again to avoid stale references...'''
        transfer_modal = self.driver.find_element(By.ID, 'transferNewModal')

        transfer_form = transfer_modal.find_element(By.XPATH, './/form')
        transfer_form_inputs = transfer_form.find_elements(By.XPATH, './div')

        self.logger.info(f'Selecting outbound store: {transfer.destination}')
        store_to_select = transfer_form_inputs[2].find_element(By.XPATH, './/div[@class="search ember-view input-select-searchable"]')
        store_to_select.click()

        time.sleep(2)
    
        options = self.driver.find_elements(By.XPATH, './/li[@class="select2-results__option"]')
        for option in options:
            choice_id_full = option.get_attribute('data-select2-id')
            choice_id = choice_id_full.split('-')[-1]
            if choice_id == self.stores[transfer.destination]:
                choice = self.driver.find_element(By.XPATH, f'//li[@data-select2-id="{choice_id_full}"]')
                choice.click()
                break

        time.sleep(4)
        return
    
    def _submit_transfer(self) -> None:
        self.logger.info('Submitting transfer form.')
        WebDriverWait(self.driver, 120).until(EC.element_to_be_clickable((By.ID, 'transferNewModal')))
        transfer_modal        = self.driver.find_element(By.ID, 'transferNewModal')
        transfer_modal_footer = transfer_modal.find_element(By.XPATH, './/div[@class="modal-footer "]')

        submit_button = transfer_modal_footer.find_elements(By.TAG_NAME, 'button')[1]
        submit_button.click()

        time.sleep(4)
        return
    
    def _input_transfer_items(self, transfer: Transfer) -> None:
        self.logger.info(f'Starting input for {len(transfer.transfer_items)} transfer items.')

        for item in transfer.transfer_items:
            if float(item.quantity) <= 0: return # Skip items that weren't transferred.
            try:
                self.logger.info(f'Adding transfer item: {item.name} ({item.quantity})')
                self._add_transfer_item(item)
            except Exception as e:
                self.logger.warning(f'Failed to add item {item.name}: {e}', exc_info=True)
        
        self.logger.info('All items processed.')
        return
    
    def _add_transfer_item(self, item) -> None:

        self.logger.debug(f'Clicking "Add Transfer Line" button for {item.name}.')
        # Click the add-item button
        page_body = self.driver.find_element(By.XPATH, './/div[@class="card-body"]')
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//a[text()="Add Transfer Line"]')))
        add_item_button = page_body.find_element(By.XPATH, '//a[text()="Add Transfer Line"]')
        add_item_button.click()

        time.sleep(2)

        # Enter the item name   
        item_input = self.driver.find_element(By.ID, 'typeahead')
        item_input.send_keys(item.name)

        # WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, './/div[@class='input-group input-typeahead-container input-group-merge']')))
        time.sleep(6)
        # Select the item from the dropdown

        item_choice_container = self.driver.find_element(By.XPATH, './/div[@class="input-group input-typeahead-container input-group-merge"]')
        item_choices          = item_choice_container.find_elements(By.XPATH, './following-sibling::div/div[@class="input-type-ahead "]/div[@class="input-type-ahead-row"]')
        item_chosen = False
        for pos, i in enumerate(item_choices):
            item_choice = i.text.split(' ')
            item_choice = ' '.join(item_choice[:-1])
            print(item_choice, flush=True)
            if item_choice == item.name:
                item_choices[pos].click()
                item_chosen = True
                break
            
        if not item_chosen:
            item_choices[0].click()
        
        transfer_modal           = self.driver.find_element(By.ID, 'transferItemModal')
        transfer_form            = transfer_modal.find_element(By.XPATH, './/form')
        quantity_input_container = transfer_form.find_elements(By.XPATH, './div')[2]
        quantity_input           = quantity_input_container.find_element(By.XPATH, './/input')

        quantity_input.send_keys(Keys.BACKSPACE)
        quantity_input.send_keys(item.quantity)
        time.sleep(3)

        for attempt in range(3):
            try:
                add_transfer_item_button = self.driver.find_element(By.XPATH, './/button[text()="Add Transfer Line"]')
                add_transfer_item_button.click()
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, './/div[@class="_c-notification__content"][text()="Successfully added a Transfer Line"]')))
                self.logger.info(f'Item {item.name} addedd successfully.')
                break
            except Exception as e:
                self.logger.info(f'Attempt {attempt+1} failed for {item.name}: {e}')
                # self.logger.info('Closing add-item window and trying again.')
                # back_button = self.driver.find_element(By.XPATH, './/button[text()='Back']')
                # back_button.click()


            
        return

# endregion

# region ---- Audit Downloading -------------------------

    def get_audit_store_name(self, store: str) -> str:
        store_audit_name_map = {
            'Bakery':       'Ithaca Bakery - Meadow St',
            'Triphammer':   'Ithaca Bakery - Triphammer Rd',
            'Collegetown':  'Collegetown Bagels - College Ave',
            'Easthill':     'Collegetown Bagels - East Hill Plaza',
            'Downtown':     'Collegetown Bagels - State St',
            'Syracuse':     'Collegetown Bagels - Syracuse',
        }

        return store_audit_name_map.get(store, '')

    def _set_audit_stores_filter(self, stores: list[str]) -> None:
            
        self.logger.info(f'Setting audit "Stores" filter: {stores}')

        # Access dropdown menu
        if not (stores_dropdown := self.wait_for_element(
            locator=(By.XPATH, '//button[text()="Stores"]'))
            ):
            self.logger.error('Unable to find store selection filter.')
            raise TimeoutException('Stores filter dropdown did not load in time.')
        
        stores_dropdown.click()

        # Clear the dropdown filter
        if not (all_stores_option := self.wait_for_element(
            locator=(By.XPATH, f'//div[text()="All Stores"]'),
            condition='clickable'
        )):
            self.logger.error('Unable to find "All Stores" in dropdown filter.')
            raise TimeoutError('"All Stores" option was not clickable in time.')
        all_stores_option.click()
        time.sleep(1)
        all_stores_option.click()

        # Access dropdown filter input
        if not (input_element := self.wait_for_element(
            locator=(By.ID, 'text-input')
        )):
            self.logger.error('Unable to find store filter input element.')
            raise TimeoutError('Stores filter input box did not load in time.')
        
        # Select stores
        for store in stores:

            # Input store name
            store_audit_name = self.get_audit_store_name(store)
            input_element.clear()
            input_element.send_keys(store_audit_name)

            # Check for store option
            if not (dropdown_option := self.wait_for_element(
                locator=(By.XPATH, f'//div[text()="{store_audit_name}"]')
            )):
                self.logger.error('Unable to find inputted store; skipping.')
                continue
            
            # Click store option
            dropdown_option.click()
            time.sleep(1)

        self.logger.info('Stores filter updated successfully.')

    def _change_calendar_to_date(self, calendar, date: datetime) -> None:

        date = string_to_datetime(date)
        
        try:
            self.logger.debug('Attempting to open flatpickr calendar.')
            calendar.click()
            WebDriverWait(calendar, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flatpickr-calendar')))
        except:
            self.logger.error('Calendar did not open when clicked.')

        self.logger.debug('Calendar opened successfully.')
        time.sleep(5)

        calendar_current_month      = calendar.find_element(By.CLASS_NAME, 'cur-month')
        calendar_current_year_input = calendar.find_element(By.CLASS_NAME, 'cur-year')

        # calendar_current_year_input.send_keys(date.year)

        # print(calendar_current_month.text, flush=True)
        current_month_value = self._get_month_value(calendar_current_month.text)
        # print(f'Current calendar month {current_month_value}.', flush=True)
        # print(f'Inputted date month {date.month}.', flush=True)

        time.sleep(5)
        if current_month_value != date.month:
            # print('Changing month', flush=True)
            if current_month_value > date.month:
                # Click back
                for _ in range(current_month_value - date.month):
                    previous_month_button = calendar.find_element(By.CLASS_NAME, 'flatpickr-prev-month')
                    previous_month_button.click()
                    time.sleep(1)
            if current_month_value < date.month:
                for _ in range(date.month - current_month_value):
                    next_month_button = calendar.find_element(By.CLASS_NAME, 'flatpickr-next-month')
                    next_month_button.click()
                    time.sleep(1)

        day_container = calendar.find_element(By.CLASS_NAME, 'dayContainer')
        today = day_container.find_element(By.XPATH, f'.//span[@class="flatpickr-day "][text()="{date.day}"]')
        today.click()
        time.sleep(10)

    def _set_date_filters(self, start_date: str, end_date: str) -> None:
        
        self.logger.info(f'Setting audit "Date" filters: {start_date} to {end_date}.')

        from_date_filter = self.driver.find_element(By.XPATH, '//div[label[text()="From Date"]]')
        to_date_filter = self.driver.find_element(By.XPATH, '//div[label[text()="To Date"]]')

        self._change_calendar_to_date(from_date_filter, start_date)
        self._change_calendar_to_date(to_date_filter, end_date)

        self.logger.info('Date filters updated successfully.')

    def _submit_audit_filters(self) -> None:

        self.logger.info('Submitting audit filters.')
        submit_button = self.driver.find_element(By.XPATH, '//button[text()="Go"]')
        submit_button.click()

    def _audit_table_is_ready(self) -> bool:
        # Wait until the table header is interactable (signals table fully initialized)
        if not (sort_hdr := self.wait_for_element(
            locator=(By.CLASS_NAME, "sort-header"),
            timeout=30,
            condition="clickable",
        )):
            self.logger.error("Audit list table did not become clickable within 30s.")
            raise TimeoutException("Audit list table did not load in time.")

        self.logger.debug('Table header is clickable; table seems to have loaded successfully.')

        # Ensure table element is visible
        if not (audit_table := self.wait_for_element(
            locator=(By.TAG_NAME, "table"),
            timeout=10,
            condition="visible",
        )):
            self.logger.error("Audit table element not found/visible.")
            raise NoSuchElementException("Audit table element missing or hidden.")
        
        return True

    def _download_audits_from_table(self) -> None:

        audit_table_rows = self.driver.find_elements(By.TAG_NAME, 'tr') # Only 1 table on the page
        table_cols = ['Store', 'Date', 'Audit Closed Time', 'Auditor', 'Type', 'Inventory']

        for pos, row in enumerate(audit_table_rows):
            self.logger.info(f'Processing row {pos+1} of {len(audit_table_rows)}.')
            cols = row.find_elements(By.TAG_NAME, 'td')
            store, date, closed_time, auditor, audit_type, inventory_cost = cols

            date_hyperlink = date.find_element(By.TAG_NAME, 'a')

            original_tab = self.driver.current_window_handle

            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).click(date_hyperlink).key_up(Keys.CONTROL).perform()

            # self.driver.execute_script("window.open(arguments[0].href, '_blank');", date_hyperlink)
            time.sleep(5)

            self.driver.switch_to.window(self.driver.window_handles[-1])

            # download_filename = f'{store.text} - Foodager - Audit {date[-1:-5]}-{date[0:2]}-{date[3:5]}.xlsx'
            try:
                time.sleep(5)
                self.logger.info(f'Attempting download of row {pos+1}.')
                download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
                download_button.click()
                time.sleep(15)
                self.logger.info('Download success')
                self.driver.close()
            except:
                self.logger.info('Unable to download audit, skipping.')
            
            self.driver.switch_to.window(self.driver.window_handles[0])
            time.sleep(2)




    @SeleniumBotMixin.with_session(login=True)
    @Logger.log_exceptions
    def download_audits(self, stores: list[str], start_date: str, end_date: str) -> None:

        # store_audit_name = self.get_audit_store_name(store)

        self.logger.info('Beginning audit download.')
        
        # Navigate to audit page
        director_audit_url = self.site_map['audit_page']
        self.driver.get(director_audit_url)

        try:
            self._audit_table_is_ready() # If this fails, expect NoSuchElement or Timeout Exception
        except (TimeoutException, NoSuchElementException):
            raise 
        except: 
            raise ValueError('Something went wrong')
        
        # Set filters
        self.logger.info(
            'Setting audit options:'
            f'- stores = {[i for i in stores]}'
            f'- start_date = {start_date}'
            f'- end_date = {end_date}'
        )

        # Set filters
        try:
            self._set_audit_stores_filter(stores)
            self._set_date_filters(start_date, end_date)
            self._submit_audit_filters()
            time.sleep(3)
            self._audit_table_is_ready()
        except:
            raise ValueError()
        
        # Download Filtered Audits
        try:
            self._download_audits_from_table()
        except:
            raise ValueError()









        # time.sleep(10)
        # try:
        #     audit_list_table = self.driver.find_element(By.TAG_NAME, 'table')
        #     self.logger.info('Audit table loaded.')
        # except:
        #     self.logger.info('Could not find audit list table, ending audit download.')
        #     raise ValueError()
        
        # # Set to correct store(s)
        # try:
        #     stores_dropdown = self.driver.find_element(By.XPATH, '//button[text()="Stores"]')
        #     stores_dropdown.click()
        #     time.sleep(5)

        #     all_stores_option = self.driver.find_element(By.XPATH, f'//div[text()="All Stores"]')
        #     time.sleep(1)
        #     all_stores_option.click()
            # time.sleep(1)
            # all_stores_option.click()
            # time.sleep(1)
            # for store in stores:
            #     store_text_input = self.driver.find_element(By.ID, 'text-input')
            #     store_text_input.clear()
            #     store_text_input.send_keys(store_audit_name)
            #     time.sleep(2)
            #     dropdown_option = self.driver.find_element(By.XPATH, f'//div[text()="{store_audit_name}"]')

            #     # NEED TO CHECK IF STORE IS ALREADY TOGGLED
            #     dropdown_option.click()
            #     time.sleep(2)

        # except:
        #     raise ValueError()
        # # Set starting date
        # # Set ending date
        # try:
        #     self.logger.info('Searching for table rows.')
        #     audit_rows = audit_list_table.find_elements(By.TAG_NAME, 'tr')
        #     self.logger.info('Table rows found.')
        # except:
        #     self.logger.info('Unable to find table rows, ending audit download.')
        #     raise ValueError()
        
        # self.logger.info(f'Found {len(audit_rows)} rows.')
        # for pos, row in enumerate(audit_rows):
        #     self.logger.info(f'Processing row {pos+1} of {len(audit_rows)}.')
        #     cols = row.find_elements(By.TAG_NAME, 'td')
        #     store, date, closed_time, auditor, audit_type, inventory_cost = cols

        #     date_hyperlink = date.find_element(By.TAG_NAME, 'a')

        #     original_tab = self.driver.current_window_handle

        #     actions = ActionChains(self.driver)
        #     actions.key_down(Keys.CONTROL).click(date_hyperlink).key_up(Keys.CONTROL).perform()

        #     # self.driver.execute_script("window.open(arguments[0].href, '_blank');", date_hyperlink)
        #     time.sleep(5)

        #     self.driver.switch_to.window(self.driver.window_handles[-1])
        #     time.sleep(5)

        #     # download_filename = f'{store.text} - Foodager - Audit {date[-1:-5]}-{date[0:2]}-{date[3:5]}.xlsx'
        #     try:
        #         time.sleep(5)
        #         self.logger.info(f'Attempting download of row {pos+1}.')
        #         download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
        #         download_button.click()
        #         time.sleep(5)
        #         self.logger.info('Download success')
        #     except:
        #         self.logger.info('Unable to download audit, skipping.')
        #         self.driver.close()

            

            # self.driver.close()
            # self.driver.switch_to.window(original_tab)
            



# endregion
    

    '''HELPER FUNCTIONS'''
    
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
    def _scrape_order(self) -> list[OrderItem]:
        order_table = self.driver.find_element(By.TAG_NAME, 'tbody')
        item_rows   = order_table.find_elements(By.TAG_NAME, 'tr')

        items = []
        for item in item_rows:
            item_info = item.find_elements(By.TAG_NAME, 'td')
        
            item_sku   = item_info[2].text
            item_name  = item_info[3].find_element(By.XPATH, './/a').text
            quantity   = item_info[5].text
            cost_per   = item_info[6].text.replace('$', '').replace(',', '')
            total_cost = item_info[7].text.replace('$', '').replace(',', '')

            items.append(OrderItem(
                item_sku, 
                item_name, 
                quantity, 
                cost_per, 
                total_cost
            ))
            
        return items
    
    '''
    Assumes the current driver is 'looking at' an order page.

    Clicks the download button on the order page.
    '''
    def _download_order_pdf(self) -> None:
        download_button = self.driver.find_element(By.CLASS_NAME, 'fa-download')
        ActionChains(self.driver).key_down(Keys.CONTROL).click(download_button).perform()
        return
       
    def _update_existing_order(self, order: Order) -> bool:
        '''
        Requests that the OrderCoordinator handle the update check and replacement
        if the new order differs from the existing one.

        Returns True if the file is identical (no update needed),
        False if the new file should be written.
        '''
        self.logger.info(f'[Order Update] Initiating update protocol for {order.store} / {order.vendor} / {order.date}.')
        return self.order_coordinator.check_and_update_order(order)

    def _change_calendar_date(self, transfer_datetime: datetime) -> None:
       
        try:
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flatpickr-calendar')))
        except:
            print('Calendar not found.', flush=True)

        print('Checking year, month, and days.', flush=True)
        calendar_current_month      = self.driver.find_element(By.CLASS_NAME, 'cur-month')
        calendar_current_year_input = self.driver.find_element(By.CLASS_NAME, 'cur-year')

        calendar_current_year_input.send_keys(transfer_datetime.year)

        current_month_value = self._get_month_value(calendar_current_month.text)
        # desired_month_value = self._get_month_value(transfer_datetime.month)

        # print(current_month_value, flush=True)
        # print(desired_month_value, flush=True)
        if current_month_value != transfer_datetime.month:
            print('Changing month', flush=True)
            if current_month_value > transfer_datetime.month:
                # Click back
                for _ in range(current_month_value - transfer_datetime.month + 1):
                    previous_month_button = self.driver.find_element(By.CLASS_NAME, 'flatpickr-prev-month')
                    previous_month_button.click()
                    time.sleep(1)
            if current_month_value < transfer_datetime.month:
                for _ in range(transfer_datetime.month - current_month_value + 1):
                    next_month_button = self.driver.find_element(By.CLASS_NAME, 'flatpickr-next-month')
                    next_month_button.click()
                    time.sleep(1)

        calendar = self.driver.find_element(By.CLASS_NAME, 'dayContainer')
        today = calendar.find_element(By.XPATH, f'.//span[@class="flatpickr-day "][text()="{transfer_datetime.day}"]')
        today.click()
        time.sleep(2)

        return
    
    def _get_month_value(self, month: str) -> int:
        # print(month, flush=True)
        months = {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5, 
            'June': 6, 
            'July': 7, 
            'August': 8, 
            'September': 9, 
            'October': 10, 
            'November': 11, 
            'December': 12
        }

        
        if month not in months: return  None
        return months[month] 