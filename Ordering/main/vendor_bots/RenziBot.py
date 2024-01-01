import main.vendor_bots.VendorBot as VendorBot
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver

class RenziBot(VendorBot):

    def __init__(self, driver: webdriver, username, password) -> None:
        self.driver = driver
        self.username = username
        self.password = password

        self.store_ids = {
            'Bakery': "11104",
            'Collegetown': "11106",
            'Triphammer': "11105",
            'Easthill': "11108",
            'Downtown': "11107"
        }

    def login(self) -> None:
	
        self.driver.get('https://connect.renzifoodservice.com/pnet/eOrder')
        
        username_input = self.driver.find_element(By.NAME, 'UserName')
        password_input = self.driver.find_element(By.NAME, 'Password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        submit_button = self.driver.find_element(By.NAME, 'SubmitBtn')
        submit_button.click()
        time.sleep(5)

        return

    def switch_store(self, store_id: str) -> None:

        store_dropdown = self.driver.find_element(By.NAME, 'selectedCustomer')
        store_dropdown.click()

        time.sleep(3)

        store_id = f'  1,  1,  1,{store_id}'
        store_option = Select(store_dropdown.find_element(By.XPATH, f'.//option[value="{store_id}"]'))
        store_option.select_by_value(store_id)

        time.sleep(3)

        return
