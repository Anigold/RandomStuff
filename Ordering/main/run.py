from craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
from os import getenv
from selenium import webdriver

download_folder_path = '~/Downloads/'
options = uc.ChromeOptions()
preferences = {
    "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    "download.default_directory": f'{download_folder_path}',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", preferences)
driver = uc.Chrome(options=options, use_subprocess=False)

dotenv = load_dotenv()

username = getenv('CRAFTABLE_USERNAME')
password = getenv('CRAFTABLE_PASSWORD')

stores = [
#     'DOWNTOWN',
#     'EASTHILL',
#     'TRIPHAMMER',
#     'BAKERY'
     'COLLEGETOWN'
]

if __name__ == '__main__':
    craft_bot = CraftableBot(driver, username, password)

    craft_bot.login()

    for store in stores:
        craft_bot.get_orders(store, '12/31/2023')

    time.sleep(20)
    craft_bot.close_session()