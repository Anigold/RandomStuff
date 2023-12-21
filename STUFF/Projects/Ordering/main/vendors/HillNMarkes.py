import Vendor
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc


class HillNMarkes(Vendor):

    def login(driver, username: str, password: str, store_id: str) -> None:
	
        driver.get('https://www.hillnmarkes.com/Welcome.action')

        print('Finding login dropdown...')
        login_dropdown_button = driver.find_elements(By.CLASS_NAME, 'dropdown-toggle')
        login_dropdown_button[0].click()
        print('...login dropdown found.')

        print('')
        time.sleep(2)

        print('Finding login form...')
        login_form = driver.find_element(By.ID, 'popLoginForm')
        username_form = driver.find_element(By.ID, 'popUserName')
        password_form = driver.find_element(By.ID, 'popPassword')
        print('...login form found.')

        print('')

        print('Sending login information...')
        username_form.send_keys(username)
        password_form.send_keys(temp_password)
        login_form.find_element(By.XPATH, './/button[@type="submit"]').click()
        print('...credentials sent.')

        time.sleep(10)
        print('')

        print('Selecting store...')
        store_selection_table = driver.find_element(By.ID, 'example')
        store_rows = store_selection_table.find_elements(By.XPATH, './/tbody/tr')


        # Choosing IB for testing
        store_rows[store_id].find_element(By.XPATH, './/td').click()
        time.sleep(10)
        print('...store selected.')

        print('')

        print('Waiting for login success...')

        return

    