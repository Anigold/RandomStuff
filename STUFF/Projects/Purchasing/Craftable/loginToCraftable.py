
core_url = 'https://app.craftable.com'
username = 'goldsmithnandrew@gmail.com'
password = 'nW#1$e1w3Ez'

ctb  = '14372'
dtb  = '14373'
etb  = '14374'
trip = '14375'
ib 	 = '14376'

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

if __name__ == '__main__':
	
	# Initialize the WebDriver (replace 'chromedriver' with the path to your driver)
	service = Service(executable_path='C:/Users/Will/Desktop/Andrew/Projects/Purchasing/Craftable/chromedriver-win32/chromedriver.exe')
	options = webdriver.ChromeOptions()
	driver  = webdriver.Chrome(service=service, options=options)

	# Navigate to a website
	driver.get(core_url)

	time.sleep(3)

	email_field    = driver.find_element('xpath', '//input[@type="email"]')
	password_field = driver.find_element('xpath', '//input[@type="password"]')
	submit_button  = driver.find_element('xpath', '//button[@type="submit"]')

	email_field.send_keys(username)
	password_field.send_keys(password)
	submit_button.click()

	time.sleep(10)

	# Switch to store
	driver.get(core_url + '/buyer/2/' + ctb)
	time.sleep(5)

	# Go to audit page
	driver.get(core_url + '/buyer/2/' + ctb + '/audit/menu')
	time.sleep(5)

	# Find audit button
	new_audit_button = driver.find_element('xpath', '//a[text()="Start New Audit"]')
	new_audit_button.click()
	time.sleep(3)

	partial_audit_radio_button = driver.find_element('xpath', '//input[@value="partial"]')
	partial_audit_radio_button.click()
	time.sleep(3)

	# Start audit
	new_audit_button = driver.find_element('xpath', '//button[text()="Start New Audit"]')
	new_audit_button.click()
	time.sleep(3)

	# Find items in table
	table_rows = driver.find_elements('xpath', '//table/tbody/tr')
	for i in table_rows:
		print(i.find_element('xpath', 'td[2]/a').get_attribute('text'))

	time.sleep(2)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
	
	time.sleep(20)
	driver.quit()
