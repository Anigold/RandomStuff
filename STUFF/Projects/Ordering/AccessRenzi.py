from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import undetected_chromedriver as uc

driver = uc.Chrome(use_subprocess=True)
username = '11104'
temp_password = 'IB11104!!' 

store_ids = {
	'Bakery': "11104",
	'Collegetown': "11106",
	'Triphammer': "11105",
	'Easthill': "11108",
	'Downtown': "11107"
}

def login(driver, username: str, password: str) -> None:
	
	driver.get('https://connect.renzifoodservice.com/pnet/eOrder')
	
	username_input = driver.find_element(By.NAME, 'UserName')
	password_input = driver.find_element(By.NAME, 'Password')

	username_input.send_keys(username)
	password_input.send_keys(password)

	submit_button = driver.find_element(By.NAME, 'SubmitBtn')
	submit_button.click()
	time.sleep(5)

	return

def switch_store(driver, store_id) -> None:

	store_dropdown = driver.find_element(By.NAME, 'selectedCustomer')
	store_dropdown.click()

	time.sleep(3)

	store_id = f'  1,  1,  1,{store_id}'
	store_option = Select(store_dropdown.find_element(By.XPATH, f'.//option[value="{store_id}"]'))
	store_option.select_by_value(store_id)

	time.sleep(3)

	return




if __name__ == '__main__':

	login(driver, username, temp_password)

	switch_store(driver, '11106')



	time.sleep(50)
	driver.close()