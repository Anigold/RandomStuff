from craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
from os import getenv
from selenium import webdriver
from os import listdir, remove, mkdir, rename
from os.path import isfile, join, isdir
from helpers import CraftableToUsable

dotenv = load_dotenv()

username = getenv('CRAFTABLE_USERNAME')
password = getenv('CRAFTABLE_PASSWORD')
download_path = getenv('ORDER_DOWNLOAD_PATH')

options = uc.ChromeOptions()
preferences = {
    "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    "download.default_directory": f'{download_path}',
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
    "plugins.always_open_pdf_externally": True,
    "download.directory_upgrade": True,
}
options.add_experimental_option("prefs", preferences)
driver = uc.Chrome(options=options, use_subprocess=True)

stores = [
    'DOWNTOWN',
    'EASTHILL',
    #'TRIPHAMMER',
    #'BAKERY',
    'COLLEGETOWN'
]

def get_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file))]

def sort_orders(path: str) -> None:
    # Sort and group orders
    files = get_files(path)
    for file in files:
        
        vendor_name = file.split('_')[0].strip()

        if not isdir(f'{path}{vendor_name}'):
            mkdir(f'{path}{vendor_name}')
        
        rename(f'{path}{file}', f'{path}{vendor_name}\\{file}')
    return

if __name__ == '__main__':
    # craft_bot = CraftableBot(driver, username, password)

    # craft_bot.login()

    # for store in stores:
    #     craft_bot.get_all_orders(store)

    # sort_orders(download_path)

    CraftableToUsable.craftable_pdf_to_excel(f'{download_path}')

    time.sleep(20)
    #craft_bot.close_session()