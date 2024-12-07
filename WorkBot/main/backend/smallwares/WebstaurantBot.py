from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains 
import time
from pynput.keyboard import Key, Controller
from os import rename
from pprint import pprint
from os import listdir, remove as os_remove, mkdir, rename
from os.path import isfile, join, isdir
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
from os import getenv
import pprint

from openpyxl import Workbook

from backend.transferring import Transfer
import calendar
from datetime import date, datetime

from openpyxl import load_workbook

dotenv = load_dotenv()

SOURCE_PATH = getenv('SOURCE_PATH')
COMPLETED_INVOICES_PATH = f'{SOURCE_PATH}\\backend\\smallwares\\invoices\\completed'
DOWNLOAD_PATH = f'{SOURCE_PATH}\\backend\\downloads'

class WebstaurantBot:

    def __init__(self, driver, username, password):
        self.driver        = driver
        self.username      = username
        self.password      = password

        self.is_logged_in = False

    def login(self) -> None:
        
        if self.is_logged_in: return

        self.driver.get('https://www.webstaurantstore.com/myaccount/')

        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'loginForm')))

        username_form = self.driver.find_element(By.ID, 'email')
        password_form = self.driver.find_element(By.ID, 'password')

        username_form.send_keys(self.username)
        password_form.send_keys(self.password)

        login_button = self.driver.find_element(By.ID, 'the_login_button')
        time.sleep(5)
        login_button.click()

        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, 'account__section')))

        self.is_logged_in = True
        return

    def logout(self) -> None:
        pass
 
    def go_to_orders(self) -> None:
        if not self.is_logged_in:
            self.login()

        return self.driver.get('https://www.webstaurantstore.com/myaccount/orders/')
    
    def go_to_order_page(self, order_page: int) -> None:

        if not self.is_logged_in: self.login()

        return self.driver.get(f'https://www.webstaurantstore.com/myaccount/orders?PageNumber={order_page}')
    
    def go_to_order(self, invoice_number: int) -> None:
        
        if not self.is_logged_in: self.login()

        return self.driver.get(f'https://www.webstaurantstore.com/myaccount/orders/details/{invoice_number}')
    
    def get_order_info(self, invoice_number: int, download_invoice=False) -> dict:

        self.go_to_order(invoice_number)
        time.sleep(5)

        # Ensure we're looking at items and not tracking info
        item_tab = self.driver.find_element(By.XPATH, './/a[@class="tab__link"][text()="Items"]')
        item_tab.click()
        time.sleep(4)

        order = {}
        '''
        order = {
            order_number
            date
            order_items
        }
        '''

        order_items = []
        '''
        order_item = {
            name
            sku
            quantity
            price
            total_cost
        }
        '''
        order_summary_card = self.driver.find_element(By.CLASS_NAME, 'order__summary')
        order_date         = order_summary_card.find_element(By.CLASS_NAME, 'panel__header-subheader').text
        print(order_date, flush=True)
        order_date = order_date.replace('Placed: ', '')
        print(order_date, flush=True)
        item_list_table      = self.driver.find_element(By.ID, 'orderItems') # This is organized by location and then items.
        order_item_locations = item_list_table.find_elements(By.CLASS_NAME, 'order__tracking-location')

        for order_item_location in order_item_locations:
            item_info_table = order_item_location.find_element(By.TAG_NAME, 'tbody')
            item_info       = item_info_table.find_elements(By.TAG_NAME, 'tr')
            for item in item_info:

                name       = item.find_element(By.CLASS_NAME, 'itemlist__title').text
                sku        = item.find_element(By.CLASS_NAME, 'itemlist__sku').text
                quantity   = item.find_element(By.CLASS_NAME, 'itemlist__qty').text
                price      = item.find_element(By.CLASS_NAME, 'itemlist__subtotal').text
                total_cost = item.find_element(By.CLASS_NAME, 'itemlist__total').text

                order_item = {
                    'name': name,
                    'sku': sku,
                    'quantity': quantity,
                    'price': price,
                    'total_cost': total_cost
                }

                order_items.append(order_item)

        order = {
            'order_number': invoice_number,
            'order_date': order_date,
            'order_items': order_items,
        }

        if download_invoice:
            download_button = self.driver.find_element(By.CLASS_NAME, 'icon-download')
            download_button.click()
            time.sleep(2)

            rename(f'{DOWNLOAD_PATH}\\{invoice_number}.pdf', f'{SOURCE_PATH}\\backend\\smallwares\\invoices\\{invoice_number}.pdf')

        return order
    
    def get_orders_between_dates(self, start_date: date, end_date: date, order_number_only=True) -> list:
        
        self.go_to_orders()
        orders = []
        order_cards = self.driver.find_elements(By.CLASS_NAME, 'item-listing')
        order_cards.pop(0) # Remove the first instance of item-listing to skip over header
        for order_card in order_cards:
            order_date = order_card.find_element(By.CLASS_NAME, 'order-info').text
            order_date_object = datetime.strptime(order_date, '%B %d, %Y')

            if (order_date_object >= start_date) and (order_date_object <= end_date):
                if order_number_only: 
                    order_number = order_card.find_element(By.CLASS_NAME, 'control-label').text.split('#')[1]
                    orders.append(order_number)
                    continue

        return orders

    def get_all_undocumented_orders(self) -> list:

        completed_orders = set(self.get_completed_orders_list())
        orders = []
        page = 1
        finished = False
        while not finished:
            self.go_to_order_page(page)
            time.sleep(4)
            
            order_cards = self.driver.find_elements(By.CLASS_NAME, 'item-listing')
            order_cards.pop(0)
            for order_card in order_cards:
                order_number = order_card.find_element(By.CLASS_NAME, 'control-label').text.split('#')[1]
                if f'{order_number}.pdf' in completed_orders: return orders
                orders.append(order_number)

            page += 1

        return orders

    def get_completed_orders_list(self) -> list:
        return [file for file in listdir(COMPLETED_INVOICES_PATH) if isfile(join(COMPLETED_INVOICES_PATH, file))]

    def update_pick_list(self, order_info) -> None:
        workbook = load_workbook(f'{SOURCE_PATH}\\backend\\smallwares\\PickList.xlsx')
        sheet = workbook.active

        for order_item in order_info['order_items']:
            sheet.append([
                order_info['order_date'],
                order_info['order_number'],
                order_item['sku'],
                order_item['name'],
                order_item['quantity'],
                '',
                '',
                order_item['price']
            ])

        workbook.save(f'{SOURCE_PATH}\\backend\\smallwares\\PickList.xlsx')

        rename(f'{SOURCE_PATH}\\backend\\smallwares\\invoices\\{order_info['order_number']}.pdf', f'{COMPLETED_INVOICES_PATH}\\{order_info['order_number']}.pdf')

        return

    