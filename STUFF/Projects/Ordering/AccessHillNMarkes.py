from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc

driver = uc.Chrome(use_subprocess=True)
username = 'purchasing@ithacabakery.com'
temp_password = 'BAKERY90' 

store_ids = {
	'Bakery': 0,
	'Collegetown': 1,
	'Triphammer': 3,
	'Easthill': 4,
	'Downtown': 7
}

def login(driver, username: str, password: str, store: str) -> None:
	
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
	store_rows[store_ids[store]].find_element(By.XPATH, './/td').click()
	time.sleep(10)
	print('...store selected.')

	print('')

	print('Waiting for login success...')

	return


def go_to_quick_cart_file_upload(driver) -> None:
	driver.get('https://www.hillnmarkes.com/QuickCartStandard')
	return

def upload_quick_cart_file(driver, file_to_upload: str) -> None:

	if driver.current_url != 'https://www.hillnmarkes.com/QuickCartStandard':
		go_to_quick_cart_file_upload(driver)
		time.sleep(5)
		return upload_quick_cart_file(driver, file_to_upload)

	quick_order_tab = driver.find_element(By.ID, 'quickOrderTab')
	file_upload_tab = quick_order_tab.find_elements(By.XPATH, './/ul/li')[2]
	file_upload_tab.click()

	time.sleep(2)

	file_upload_form = driver.find_element(By.ID, 'uploadForm')
	file_upload_input = driver.find_element(By.ID, 'datafile')
	file_upload_input.send_keys(file_to_upload)
	file_submit = file_upload_form.find_element(By.XPATH, './/input[@type="submit"]')
	file_submit.click()
	time.sleep(5)
	return 

if __name__ == '__main__':

	login(driver, username, temp_password, 'Bakery')

	go_to_quick_cart_file_upload(driver)

	upload_quick_cart_file(driver, 'C:/Users/Will/Desktop/Andrew/Projects/Ordering/HillNMarkes Order - Downtown 12172023_order_list.xlsx')


	time.sleep(50)
	driver.close()