from craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
from os import getenv
from selenium import webdriver
from os import listdir, remove, mkdir, rename
from os.path import isfile, join, isdir
from helpers import CraftableToUsable
from vendor_bots.HillNMarkesBot import HillNMarkesBot
from vendor_bots.RenziBot import RenziBot
from vendor_bots.CopperHorseBot import CopperHorseBot
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

if __name__ == '__main__':

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
    # #order_manager = OrderManager('Easthill', 'HillNMarkes')
    # HnM_Bot   = HillNMarkesBot(None, getenv('HILLNMARKES_USERNAME'), getenv('HILLNMARKES_PASSWORD'))
    # # driver = None
    # renzi_bot = RenziBot(None, getenv('RENZI_USERNAME'), getenv('RENZI_PASSWORD'))
    # copperhorse_bot = CopperHorseBot()


    craft_bot = CraftableBot(driver, username, password)

    craft_bot.login()

    craft_bot.get_orders_from_webpage('BAKERY')
    # for store in stores:
    #     craft_bot.get_orders_from_webpage(store)

    # sort_orders('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\')

    # for vendor_bot in vendor_bots:
    #     CraftableToUsable.craftable_pdf_to_excel(f'{download_path}{vendor_bot.name}\\', vendor_bot)    

    # failures = 0
    # for i in range(0, 6, 1):
    #     print(f'Attempt #{i}.')
    #     try:
    #         options = uc.ChromeOptions()
    #         preferences = {
    #             "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    #             "download.default_directory": f'{download_path}',
    #             "download.prompt_for_download": False,
    #             "safebrowsing.enabled": True,
    #             "plugins.always_open_pdf_externally": True,
    #             "download.directory_upgrade": True,
    #         }
    #         options.add_experimental_option("prefs", preferences)
    #         driver = uc.Chrome(options=options, use_subprocess=True)
    #         renzi_bot = RenziBot(driver, getenv('RENZI_USERNAME'), getenv('RENZI_PASSWORD'))
    #         renzi_bot.retrieve_pricing_sheet('IBProduce')
    #         renzi_bot.end_session()
    #         time.sleep(5)
    #     except Exception as e:
    #         print(e)
    #         failures += 1
    #         time.sleep(5)
    # print(failures)
    # HnM_Bot.login()
    # HnM_Bot.switch_store('DOWNTOWN')
    # HnM_Bot.upload_quick_cart_file(f'{download_path}{HnM_Bot.name}\\Hill & Markes _ DOWNTOWN 01062024.xlsx')
    craft_bot.close_session()

    # CraftableToUsable.craftable_pdf_to_excel('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\Copper Horse Coffee\\', copperhorse_bot)
    #copperhorse_bot.combine_orders('C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\Ordering\\main\\orders\\OrderFiles\\Copper Horse Coffee\\')
 