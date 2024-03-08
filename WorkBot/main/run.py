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
from backend.vendor_bots.IthacaBakeryBot import IthacaBakeryBot
from backend.vendor_bots.DutchValleyBot import DutchValleyBot

from backend.orders import OrderManager

from backend.emailer.Emailer import Emailer
from backend.emailer.Services.Service import Email
from backend.emailer.Services.Outlook import Outlook

from backend.printing.Printer import Printer
from backend.transferring.Transfer import Transfer, TransferItem


from datetime import date, datetime

from openpyxl import load_workbook

dotenv = load_dotenv()

username      = getenv('CRAFTABLE_USERNAME')
password      = getenv('CRAFTABLE_PASSWORD')
download_path = getenv('DOWNLOAD_PATH') or 'C:\\Users\\golds\\projects\\WorkBot\\RandomStuff\\WorkBot\\main\\backend\\downloads\\'

ORDER_FILES_PATH = 'C:\\Users\\golds\\projects\\WorkBot\\RandomStuff\\WorkBot\\main\\backend\\orders\\OrderFiles\\'
PRICING_FILES_PATH = 'C:\\Users\\golds\\projects\\WorkBot\\RandomStuff\\WorkBot\\main\\backend\\pricing\\VendorSheets\\'

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
     
    username = getenv(f'{name.upper().replace(' ', '_')}_USERNAME') or 'No Username Found'
    password = getenv(f'{name.upper().replace(' ', '_')}_PASSWORD') or 'No Password Found'

    return {'username': username, 'password': password}

def get_excel_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.xlsx')]

def get_bot(name) -> VendorBot:
     
    bots = {
        'Renzi': RenziBot,
        'Hill & Markes': HillNMarkesBot,
        'Sysco': SyscoBot,
        'Performance Food': PerformanceFoodBot,
        'Copper Horse Coffee': CopperHorseBot,
        'UNFI': UNFIBot,
        'Ithaca Bakery': IthacaBakeryBot,
        'Dutch Valley': DutchValleyBot
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

def format_orders_for_transfer(vendor: str, path_to_folder: str) -> None:
    vendor_bot = get_bot(vendor)(None, None, None)
    excel_files = get_excel_files(f'{path_to_folder}{vendor_bot.name}\\')
    for file in excel_files:
        file_name_no_extension = file.split('.')[0]
        item_data = FormatItemData.extract_item_data_from_excel_file_for_transfer(f'{path_to_folder}{vendor_bot.name}\\{file}')
        vendor_bot.format_for_file_upload(item_data, f'{path_to_folder}{vendor_bot.name}\\Formatted _ {file_name_no_extension}')
    return

def setup_emails_for_sunday() -> None:
    sunday_emailer = Emailer(service=Outlook)
    emails = [
        {
        'subject': 'Equal Exchange Order',
        'to': 'orders@equalexchange.com',
        'body': 'Please see attached for orders, thank you!'
        },
        {
        'subject': 'Euro Cafe Order',
        'to': 'sales@eurocafeimports.com',
        'body': 'Please see attached for orders, thank you!',
        'cc': 'scott.tota@eurocafeimports.com'
        },
        {
        'subject': 'Fingerlakes Farms Order',
        'to': 'orders@ilovenyfarms.com',
        'body': 'Please see attached for orders, thank you!'
        },
        {
        'subject': 'Macro Mama Order',
        'to': 'macromamas@gmail.com',
        'body': 'Please see attached for orders, thank you!'
        },
        {
        'subject': 'Copper Horse Order',
        'to': 'copperhorsecoffee@gmail.com',
        'body': 'Please see attached for orders, thank you!'
        }
    ]

    for email in emails:
        cc = email['cc'] if 'cc' in email else None
        email_object = Email(email['to'], email['subject'], email['body'], cc=cc)
        sunday_emailer.create_email(email_object)
        sunday_emailer.display_email(email_object)

    return

def print_schedule_daily(day: int) -> None:

    schedule = {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }

    if day not in schedule:
        return None
    
    path_to_schedules = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\Schedules\\'
    printer_object = Printer()

    return printer_object.print_file(f'{path_to_schedules}{schedule[day]}.pdf')

def get_transfers() -> list:
    path = ORDER_FILES_PATH + 'Ithaca Bakery'
    return [file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.xlsx') and file.split(' _ ')[0] == 'Formatted']

if __name__ == '__main__':

    vendors = [
        # 'Renzi', 
        # 'Sysco', 
        # 'Performance Food',
        # 'UNFI',
        # 'Hill & Markes',
        # 'Copper Horse Coffee',
        # 'Johnston Paper',
        # 'Regional Distributors, Inc.',
        'Ithaca Bakery',
    ]

    stores = [
        #  'BAKERY',
         'TRIPHAMMER',
        #  'COLLEGETOWN',
         'EASTHILL',
         'DOWNTOWN'
    ]

    options = create_options()
    driver  = uc.Chrome(options=options, use_subprocess=True)

    craft_bot = CraftableBot(driver, username, password)

    craft_bot.login()

    # for store in stores:
    #     for vendor in vendors:
    #         craft_bot.get_order_from_vendor(store, vendor, download_pdf=True)
    # sort_orders(ORDER_FILES_PATH)
    # format_orders_for_transfer('Ithaca Bakery', ORDER_FILES_PATH)

    # test_transfer = Transfer('BAKERY', 'COLLEGETOWN', [{'name': 'Kilogram', 'quantity': 4}], datetime(2024, 3, 2))
    for transfer_file in get_transfers():

        store_to            = transfer_file.split(' _ ')[2].split(' ')[0]
        store_from          = 'BAKERY'
        items               = []
        date_from_file_name = transfer_file.split(' _ ')[2].split(' ')[1].split('.')[0]
        day                 = int(date_from_file_name[0:2])
        month               = int(date_from_file_name[2:4])
        year                = int(date_from_file_name[4:])

        workbook = load_workbook(f'{ORDER_FILES_PATH}Ithaca Bakery\\{transfer_file}')
        sheet = workbook.active

        for item_row in sheet.iter_rows():
            to_transfer, name, quantity = item_row

            if not to_transfer:
                continue
            
            items.append(TransferItem(name.value, quantity.value))
        
        transfer = Transfer(store_from, store_to, items, datetime(year, month, day))
        craft_bot.input_transfer(transfer)
    #

    # vendor_to_print = [
        # 'BakeMark',
        # 'Lentz',
        # "Regional Distributors, Inc.",
        # 'Johnston Paper',
        # 'DUTCH VALLEY FOOD DIST'
    # ]
    # printer = Printer()    
    # for vendor in vendor_to_print:
    #     for file in get_files(f'{ORDER_FILES_PATH}{vendor}'):
    #         if not file.endswith('pdf'): continue
    #         printer.print_file(f'{ORDER_FILES_PATH}{vendor}\\{file}')
    #         time.sleep(6)
        
    craft_bot.close_session()
    # format_orders('Performance Food', ORDER_FILES_PATH)
    # format_orders('Sysco', ORDER_FILES_PATH)
    # print_schedule_daily(3)
 
    # setup_emails_for_sunday()
    # copper_path = f'{ORDER_FILES_PATH}Copper Horse Coffee\\'

    # copper_store_string = f'Copper Horse Coffee _ % 03022024.xlsx'

    # copper_bot = CopperHorseBot()
    # copper_bot.combine_orders([f'{copper_path}{copper_store_string.replace('%', store)}' for store in stores], copper_path)
    # guide_names = ['IBProduce', 'IBFavorite']
    # for vendor in vendors:
        
    #     credentials   = get_credentials(vendor)
    #     bot           = get_bot(vendor)(driver, credentials['username'], credentials['password'])

    #     for pricing_guide in guide_names:
    #         file_name     = bot.retrieve_pricing_sheet(pricing_guide)

    #         new_file_name = f'{PRICING_FILES_PATH}{bot.name} {pricing_guide} {date.today()}.{file_name.split('.')[1]}'

    #         rename(f'{download_path}{file_name}', new_file_name)

    # ithaca_bot = get_bot('Ithaca Bakery')()
    # ithaca_path = f'{ORDER_FILES_PATH}Ithaca Bakery\\'

    # ithaca_store_string = f'Ithaca Bakery _ % 03022024.xlsx'

    # ithaca_bot.combine_orders([f'{ithaca_path}{ithaca_store_string.replace('%', store)}' for store in stores], ithaca_path)

   