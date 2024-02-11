from craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
from os import getenv
from selenium import webdriver
from os import listdir, remove, mkdir, rename
from os.path import isfile, join, isdir
from helpers import CraftableToUsable
from vendor_bots.VendorBot import VendorBot
from vendor_bots.HillNMarkesBot import HillNMarkesBot
from vendor_bots.RenziBot import RenziBot
from vendor_bots.CopperHorseBot import CopperHorseBot
from vendor_bots.PerformanceFoodBot import PerformanceFoodBot
from vendor_bots.SyscoBot import SyscoBot
from orders import OrderManager

dotenv = load_dotenv()

username      = getenv('CRAFTABLE_USERNAME')
password      = getenv('CRAFTABLE_PASSWORD')
download_path = getenv('ORDER_DOWNLOAD_PATH')

stores = [
    'DOWNTOWN',
    'EASTHILL',
    'TRIPHAMMER',
    'BAKERY',
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

def create_options() -> uc.ChromeOptions:

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
    
    return options

def get_credentials(name) -> dict:
     
    username = getenv(f'{name.upper()}_USERNAME') or 'No Username Found'
    password = getenv(f'{name.upper()}_PASSWORD') or 'No Password Found'

    return {'username': username, 'password': password}

def get_bot(name) -> VendorBot:
     
    bots = {
        'Renzi': RenziBot,
        'HillNMarkes': HillNMarkesBot,
        'Sysco': SyscoBot,
        'Performance Food': PerformanceFoodBot,
        'Copper Horse Coffee': CopperHorseBot
    }

    if name not in bots:
        return
    
    return bots[name]
     
if __name__ == '__main__':

    options = create_options()
    driver  = uc.Chrome(options=options, use_subprocess=True)

    craft_bot = CraftableBot(driver, username, password)

    craft_bot.login()

    for store in stores:
        craft_bot.get_all_orders(store)

    sort_orders('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\')

    # for vendor_bot in vendor_bots:
    #     CraftableToUsable.craftable_pdf_to_excel(f'{download_path}{vendor_bot.name}\\', vendor_bot)    

    # craft_bot.close_session()

    CraftableToUsable.craftable_pdf_to_excel('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\UNFI\\', None)
    # copperhorse_bot.combine_orders('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\Copper Horse Coffee\\')
 