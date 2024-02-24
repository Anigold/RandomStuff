from backend.craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
from selenium import webdriver

import pprint
import time
from dotenv import load_dotenv
from os import getenv
from os import listdir, remove, mkdir, rename
from os.path import isfile, join, isdir

from backend.helpers import  FormatItemData

from backend.vendor_bots.VendorBot import VendorBot
from backend.vendor_bots.HillNMarkesBot import HillNMarkesBot
from backend.vendor_bots.RenziBot import RenziBot
from backend.vendor_bots.CopperHorseBot import CopperHorseBot
from backend.vendor_bots.PerformanceFoodBot import PerformanceFoodBot
from backend.vendor_bots.SyscoBot import SyscoBot
from backend.vendor_bots.UNFI import UNFIBot

from backend.orders import OrderManager

from backend.emailer.Emailer import Emailer
from backend.emailer.Services.Service import Email
from backend.emailer.Services.Outlook import Outlook


dotenv = load_dotenv()

username      = getenv('CRAFTABLE_USERNAME')
password      = getenv('CRAFTABLE_PASSWORD')
download_path = getenv('ORDER_DOWNLOAD_PATH')

ORDER_FILES_PATH = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\backend\\orders\\OrderFiles\\'

stores = [
    # 'DOWNTOWN',
    # 'EASTHILL',
    'TRIPHAMMER',
    # 'BAKERY',
    # 'COLLEGETOWN'
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
        "plugins.plugins_list":               [{"enabled": False, "name": "Chrome PDF Viewer"}],
        "download.default_directory":         f'{download_path}',
        "download.prompt_for_download":       False,
        "safebrowsing.enabled":               True,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade":         True,
    }
    options.add_experimental_option("prefs", preferences)
    
    return options

def get_credentials(name) -> dict:
     
    if ' & ' in name: name.replace(' & ', 'N') # Special Case for Hill & Markes --> HILLNMARKES
    print(name)
    username = getenv(f'{name.upper()}_USERNAME') or 'No Username Found'
    password = getenv(f'{name.upper()}_PASSWORD') or 'No Password Found'

    return {'username': username, 'password': password}

def get_excel_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.xlsx')]

def get_bot(name) -> VendorBot:
     
    bots = {
        'Renzi': RenziBot,
        'HillNMarkes': HillNMarkesBot,
        'Sysco': SyscoBot,
        'Performance Food': PerformanceFoodBot,
        'Copper Horse Coffee': CopperHorseBot,
        'UNFI': UNFIBot
    }

    if name not in bots:
        return
    
    return bots[name]
     
def format_orders(vendor: str, path_to_folder: str) -> None:
    vendor_bot = get_bot(vendor)(None, None, None)
    excel_files = get_excel_files(f'{path_to_folder}{vendor_bot.name}\\')
    for file in excel_files:
        file_name_no_extension = file.split('.')[0]
        item_data = FormatItemData.extract_item_data_from_excel_file(f'{path_to_folder}{vendor_bot.name}\\{file}')
        vendor_bot.format_for_file_upload(item_data, f'{path_to_folder}{vendor_bot.name}\\Formatted _ {file_name_no_extension}')
    return

if __name__ == '__main__':

    vendors = [
        'Renzi', 
        # 'Sysco', 
        # 'Performance Food'
    ]

    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)

    # craft_bot = CraftableBot(driver, username, password)

    # craft_bot.login()

    # for store in stores:
    #     craft_bot.get_all_orders_from_webpage(store, download_pdf=True)
       
    # sort_orders(ORDER_FILES_PATH)

    # # for vendor_bot in vendor_bots:
    # #     CraftableToUsable.craftable_pdf_to_excel(f'{download_path}{vendor_bot.name}\\', vendor_bot)    

    # craft_bot.close_session()

   # bot           = get_bot("HillNMarkes")(None, 'ewioughwoe', None)
    
    
    # order_manager = OrderManager()
    format_orders('UNFI', ORDER_FILES_PATH)

    #format_orders('Renzi', ORDER_FILES_PATH)
    # for vendor in vendors:
    #     format_orders(vendor, ORDER_FILES_PATH)
    
   

    
    # emailer = Emailer(service=Outlook)
    # new_email = Email(
    #     to='goldsmithnandrew@gmail.com', 
    #     subject='Test Email #6',
    #     body='auehbgoiugeh.',
    #     )
    # emailer.create_email(new_email)
    # copy_of_email = emailer.get_email(new_email)
    # emailer.send_email(new_email)
    
    
