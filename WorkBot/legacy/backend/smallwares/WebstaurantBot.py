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
from pprint import pprint

from openpyxl import Workbook

from backend.transferring import Transfer
import calendar
from datetime import date, datetime

from openpyxl import load_workbook

from pathlib import Path

dotenv = load_dotenv()

SOURCE_PATH             = Path(__file__).parent.parent
COMPLETED_INVOICES_PATH = SOURCE_PATH / 'smallwares' / 'invoices' / 'completed'
DOWNLOAD_PATH           = SOURCE_PATH / 'downloads'

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
    
    def go_to_order_page(self) -> None:

        if not self.is_logged_in: self.login()

        return self.driver.get(f'https://www.webstaurantstore.com/myaccount/orders')
    
    def go_to_order(self, invoice_number: int) -> None:
        
        if not self.is_logged_in: self.login()

        return self.driver.get(f'https://www.webstaurantstore.com/myaccount/orders/details/{invoice_number}')
    
    def get_order_info(self, invoice_number: int, download_invoice=False) -> dict:

        self.go_to_order(invoice_number)
        time.sleep(5)

        date_element = self.driver.find_element(By.XPATH, '//*[contains(text(), "Placed on ")]')
        date_text = date_element.text.split('on')[1]

        items = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="individual-item"]')
        order_items = []
        for item in items:
            item_name_element = item.find_element(By.CSS_SELECTOR, 'a[data-testid="item-link"]')
            item_name = item_name_element.text

            sku_element = item_name_element.find_element(By.XPATH, 'following-sibling::p')
            sku = sku_element.text.split('#')[-1]
            # print(sku, flush=True)
            pricing_container_element = sku_element.find_element(By.XPATH, 'following-sibling::div')
            pricing_info_elements = pricing_container_element.find_elements(By.TAG_NAME, 'p')

            quantity_element = pricing_info_elements[0]
            quantity = quantity_element.text.split(':')[1]

            total_price_element = pricing_info_elements[1]
            total_price = total_price_element.text.split(':')[1]

            price_per = float(total_price.replace('$', '').replace(',', '')) / int(quantity)

            order_item = {
                'name': item_name,
                'sku': sku,
                'quantity': quantity,
                'total_cost': total_price,
                'price_per': price_per
            }

            order_items.append(order_item)


        order = {
            'order_number': invoice_number,
            'order_date': date_text,
            'order_items': order_items
        }

        if download_invoice:
            download_button = self.driver.find_element(By.CSS_SELECTOR, f'[download="{invoice_number}.pdf"]')
            download_button.click()
            time.sleep(2)

            rename( DOWNLOAD_PATH / f'{invoice_number}.pdf', SOURCE_PATH / 'smallwares' / 'invoices' / f'{invoice_number}.pdf')

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
        finished = False
        self.go_to_order_page()
        time.sleep(4)

        # Choose Last 6 Months filter
        date_filter_select_element = self.driver.find_element(By.ID, 'name')
        date_filter_dropdown = Select(date_filter_select_element)

        date_filter_dropdown.select_by_visible_text('In the Past 6 Months')
        time.sleep(2)

        filter_submit_button = self.driver.find_element(By.ID, 'filter-orders-button')
        filter_submit_button.click()
        time.sleep(3)

        while not finished:
           
            order_number_texts = self.driver.find_elements(By.CSS_SELECTOR, "[id*='dashboard-order-number-']")
            for order_element in order_number_texts:
                id_text = order_element.get_attribute('id')
                order_id = id_text.split('-')[-1]

                if f'{order_id}.pdf' in completed_orders:
                    finished = True
                    break # Break loop when we get to the first completed order.

                orders.append(order_id)

            if finished: break

            pagination_nav_element = self.driver.find_element(By.CSS_SELECTOR, 'nav[aria-label="pagination"]')
            pagination_next_page = pagination_nav_element.find_element(By.XPATH, "ul/li[last()]")
            pagination_next_page.click()
            time.sleep(3)

        return orders

    def get_completed_orders_list(self) -> list:
        return [file for file in listdir(COMPLETED_INVOICES_PATH) if isfile(join(COMPLETED_INVOICES_PATH, file))]

    def update_pick_list(self, order_info) -> None:

        workbook_path = SOURCE_PATH / 'smallwares' / 'PickList.xlsx'
        workbook = load_workbook(workbook_path)
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
                order_item['price_per']
            ])

        workbook.save(workbook_path)

        rename( SOURCE_PATH / 'smallwares' / 'invoices' / f'{order_info["order_number"]}.pdf', COMPLETED_INVOICES_PATH / f'{order_info["order_number"]}.pdf')

        return

    