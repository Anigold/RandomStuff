from backend.craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
from selenium import webdriver

import pprint
import time
from dotenv import load_dotenv
from os import getenv
from os import listdir, remove as os_remove, mkdir, rename
from os.path import isfile, join, isdir

from backend.helpers import  FormatItemData

from backend.vendor_bots.VendorBot import VendorBot
from backend.vendor_bots.HillNMarkesBot import HillNMarkesBot
from backend.vendor_bots.RenziBot import RenziBot
from backend.vendor_bots.CopperHorseBot import CopperHorseBot
from backend.vendor_bots.PerformanceFoodBot import PerformanceFoodBot
from backend.vendor_bots.SyscoBot import SyscoBot
from backend.vendor_bots.UNFIBot import UNFIBot
from backend.vendor_bots.IthacaBakeryBot import IthacaBakeryBot
from backend.vendor_bots.DutchValleyBot import DutchValleyBot
from backend.vendor_bots.CortlandProduceBot import CortlandProduceBot
from backend.vendor_bots.BehlogProduceBot import BehlogProduceBot
from backend.vendor_bots.RussoProduceBot import RussoProduceBot

from backend.orders import OrderManager

from backend.emailer.Emailer import Emailer
from backend.emailer.Services.Service import Email
from backend.emailer.Services.Outlook import Outlook

from backend.printing.Printer import Printer
from backend.transferring.Transfer import Transfer, TransferItem
from backend.pricing.PriceComparator import PriceComparator

from datetime import date, datetime

from openpyxl import load_workbook

dotenv = load_dotenv()

CRAFTABLE_USERNAME = getenv('CRAFTABLE_USERNAME')
CRAFTABLE_PASSWORD = getenv('CRAFTABLE_PASSWORD')

SOURCE_PATH = getenv('SOURCE_PATH')

ORDER_FILES_PATH   = f'{SOURCE_PATH}\\backend\\orders\\OrderFiles'
PRICING_FILES_PATH = f'{SOURCE_PATH}\\backend\\pricing'
DOWNLOAD_PATH      = f'{SOURCE_PATH}\\backend\\downloads'

def get_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file))]

def sort_orders(path: str) -> None:
    # Sort and group orders
    files = get_files(path)
    for file in files:
        
        vendor_name = file.split('_')[0].strip()

        if not isdir(f'{path}\\{vendor_name}'):
            mkdir(f'{path}\\{vendor_name}')
        
        rename(f'{path}\\{file}', f'{path}\\{vendor_name}\\{file}')
    return

def create_options() -> uc.ChromeOptions:

    options = uc.ChromeOptions()
    preferences = {
        "plugins.plugins_list":               [{"enabled": False, "name": "Chrome PDF Viewer"}],
        "download.default_directory":         f'{DOWNLOAD_PATH}',
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
        'Dutch Valley': DutchValleyBot,
        'Cortland Produce Inc.': CortlandProduceBot,
        'Behlog Produce': BehlogProduceBot,
        'Russo Produce': RussoProduceBot,
    }

    if name not in bots:
        return
    
    return bots[name]
     
def format_orders(vendor: str, path_to_folder: str) -> None:
    vendor_bot  = get_bot(vendor)()
    excel_files = get_excel_files(f'{path_to_folder}\\{vendor_bot.name}\\')
    for file in excel_files:
        file_name_no_extension  = file.split('.')[0]
        item_data               = FormatItemData.extract_item_data_from_excel_file(f'{path_to_folder}\\{vendor_bot.name}\\{file}')
        vendor_bot.format_for_file_upload(item_data, f'{path_to_folder}\\{vendor_bot.name}\\Formatted _ {file_name_no_extension}')
    return

def format_orders_for_transfer(vendor: str, path_to_folder: str) -> None:
    vendor_bot  = get_bot(vendor)()
    excel_files = get_excel_files(f'{path_to_folder}\\{vendor_bot.name}\\')
    for file in excel_files:
        file_name_no_extension = file.split('.')[0]
        item_data = FormatItemData.extract_item_data_from_excel_file_for_transfer(f'{path_to_folder}\\{vendor_bot.name}\\{file}')
        vendor_bot.format_for_file_upload(item_data, f'{path_to_folder}\\{vendor_bot.name}\\Formatted _ {file_name_no_extension}')
    return

def prepare_email_to_send(email: Email) -> None:

    emailer = Emailer(service=Outlook)

    # to           = email['to'] if 'to' in email else None
    # subject      = email['subject'] if 'subject' in email else None
    # body         = email['body'] if 'body' in email else None
    # cc           = email['cc'] if 'cc' in email else None
    # attachments  = email['attachments'] if 'attachments' in email else None

    # email_object = Email(to, subject, body, cc=cc, attachments=attachments)
    
    emailer.create_email(email)
    return emailer.display_email(email)

def setup_emails_for_sunday() -> None:
    
    copper_horse_combined_order_attachment  = tuple([f'{ORDER_FILES_PATH}\\Copper Horse Coffee\\combined_order.xlsx'])
    equal_exchange_order_attachments        = tuple([join(f'{ORDER_FILES_PATH}\\Equal Exchange\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Equal Exchange\\') if isfile(join(f'{ORDER_FILES_PATH}\\Equal Exchange\\', file)) and file.endswith('.pdf')])
    finger_lakes_farms_order_attachments    = tuple([join(f'{ORDER_FILES_PATH}\\FingerLakes Farms\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\FingerLakes Farms\\') if isfile(join(f'{ORDER_FILES_PATH}\\FingerLakes Farms\\', file)) and file.endswith('.pdf')])
    euro_cafe_order_attachments             = tuple([join(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\') if isfile(join(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\', file)) and file.endswith('.pdf')])
    macro_mamas_order_attachments           = tuple([join(f'{ORDER_FILES_PATH}\\Macro Mamas\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Macro Mamas\\') if isfile(join(f'{ORDER_FILES_PATH}\\Macro Mamas\\', file)) and file.endswith('.pdf')])
    
    sunday_emailer = Emailer(service=Outlook)

    emails = [
        {
        'subject': 'Equal Exchange Order',
        'to': ['orders@equalexchange.com'],
        'body': 'Please see attached for orders, thank you!',
        'attachments': equal_exchange_order_attachments
        },
        {
        'subject': 'Euro Cafe Order',
        'to': ['sales@eurocafeimports.com'],
        'body': 'Please see attached for orders, thank you!',
        'cc': 'scott.tota@eurocafeimports.com',
        'attachments': euro_cafe_order_attachments
        },
        {
        'subject': 'Fingerlakes Farms Order',
        'to': ['orders@ilovenyfarms.com'],
        'body': 'Please see attached for orders, thank you!',
        'attachments': finger_lakes_farms_order_attachments
        },
        {
        'subject': 'Macro Mama Order',
        'to': ['macromamas@gmail.com'],
        'body': 'Please see attached for orders, thank you!',
        'attachements': macro_mamas_order_attachments
        },
        {
        'subject': 'Copper Horse Order',
        'to': ['copperhorsecoffee@gmail.com'],
        'body': 'Please see attached for orders, thank you!',
        'attachments': copper_horse_combined_order_attachment
        }
    ]

    for email in emails:
        cc              = email['cc'] if 'cc' in email else None
        attachments     = email['attachments'] if 'attachments' in email else None
        email_object    = Email(tuple(email['to']), email['subject'], email['body'], cc=cc, attachments=attachments)

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

def get_transfers(vendor: str) -> list:
    path = f'{ORDER_FILES_PATH}\\{vendor}'
    return [file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.xlsx') and file.split(' _ ')[0] == 'Formatted']

def get_day(day_of_week: str):
    days = {
        'Sunday': 0,
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6
    }

    return days[day_of_week] if day_of_week in days else None

def produce_pricing_and_email(driver) -> None:

    vendors = [
        'Renzi',
        'Sysco',
        'Performance Food'
    ]

    for vendor in vendors:
        
        credentials = get_credentials(vendor)
        bot         = get_bot(vendor)(driver, credentials['username'], credentials['password'])

        for pricing_guide in 'IBProduce':
            file_name     = bot.retrieve_pricing_sheet(pricing_guide)
            new_file_name = f'{PRICING_FILES_PATH}{bot.name} {pricing_guide} {date.today()}.{file_name.split('.')[-1]}'

            rename(f'{DOWNLOAD_PATH}{file_name}', new_file_name)

    emailer             = Emailer(service=Outlook)
    recipients          = ('kitchen.ibctb@gmail.com', 'milesbrous@gmail.com', 'mimimehaffey@gmail.com')
    produce_sheet_path  = tuple([join(f'{PRICING_FILES_PATH}', 'ProducePricing.xlsx')])
    email               = Email(recipients, 'Produce Pricing', '', cc=None, attachments=produce_sheet_path)

    emailer.create_email(email)
    emailer.display_email(email)
    return

def download_pricing_sheets(driver, vendors=['Renzi', 'Sysco', 'Performance Food', 'Cortland Produce Inc.'], guides=['IBProduce', 'IBFavorite']) -> None:

    for vendor in vendors:
        creds = get_credentials(vendor)
        bot   = get_bot(vendor)(driver, creds['username'], creds['password'])
        for pricing_guide in guides:
            file_name     = bot.retrieve_pricing_sheet(pricing_guide)
            new_file_name = f'{PRICING_FILES_PATH}\\VendorSheets\\{bot.name}_{pricing_guide}_{date.today()}.{file_name.split('.')[1]}'

            rename(f'{DOWNLOAD_PATH}\\{file_name}', new_file_name)

            bot.format_vendor_pricing_sheet(new_file_name, f'{new_file_name.rsplit('.', 1)[0]}.xlsx')
        
    return

def generate_pricing_sheets(vendors=['Renzi', 'Sysco', 'Performance Food', 'Cortland Produce Inc.', 'Russo Produce', 'Behlog Produce'], guides=['IBProduce']):
        pricer = PriceComparator()
        # pricer.item_skus_file_path = f'{PRICING_FILES_PATH}\\ItemSkus.xlsx'
        for guide in guides:
            pricer.generate_pricing_sheet(f'{PRICING_FILES_PATH}\\Templates\\{guide}.xlsx', 
                                          [f'{PRICING_FILES_PATH}\\VendorSheets\\{vendor}_{guide}_{date.today()}.xlsx' for vendor in vendors], 
                                          f'{PRICING_FILES_PATH}\\Pricing Guides\\{guide}\\{guide} {date.today()}.xlsx')
        return

def delete_all_files_without_extension(directory: str, extension: str) -> None:
    for file in listdir(directory):
        if isfile(join(directory, file)) and not file.endswith(extension):
            os_remove(f'{directory}\\{file}')
    return

if __name__ == '__main__':

    vendors = [
        'Renzi', 
        'Sysco', 
        'Performance Food',
        # 'US Foods',
        # 'UNFI',
        # 'Hill & Markes',
        # 'Copper Horse Coffee',
        # 'Johnston Paper',
        # 'Regional Distributors, Inc.',
        # 'Ithaca Bakery',
        # 'Hillcrest Foods',
        # 'BakeMark',
        # 'Lentz',
        # 'Keck\'s Food Service',
        # 'Cortland Produce Inc.',
        # 'Eurocafe Imports',
        # 'Hillcrest Dairy',
        # 'A.L. George',
        # 'BALKAN BEVERAGE LLC',
        # 'Casa',
        # 'Palmer',
        # 'Equal Exchange',
        # 'Macro Mamas',
        # 'SANICO',
        # 'Coca-Cola',
        # 'FingerLakes Farms',
        # 'ACE ENDICO',
        # 'Dawn'
    ]

    stores = [
        #  'BAKERY',
         'TRIPHAMMER',
         'COLLEGETOWN',
         'EASTHILL',
         'DOWNTOWN'
    ]

    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)

    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
    #     for store in stores: 
    #         # for vendor in vendors:
    #         #     craft_bot.get_order_from_vendor(store, vendor, download_pdf=True)
    #         craft_bot.get_all_orders_from_webpage(store, download_pdf=True)
    #     sort_orders(ORDER_FILES_PATH)

    # sort_orders(ORDER_FILES_PATH)
    # for vendor in vendors:
    #     format_orders(vendor, ORDER_FILES_PATH)
    
    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
    #     for store in stores:
    #         craft_bot.delete_all_orders(store)

    def get_all_orders_from_vendor(driver, vendor) -> None:
        stores = [
            'BAKERY',
            'TRIPHAMMER',
            'COLLEGETOWN',
            'EASTHILL',
            'DOWNTOWN'
        ]
        with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
            for store in stores: 
                craft_bot.get_order_from_vendor(store, vendor, download_pdf=True)
            sort_orders(ORDER_FILES_PATH)
        return

    def get_all_orders_from_all_stores(driver) -> None:
        stores = [
            'BAKERY',
            # 'TRIPHAMMER',
            # 'COLLEGETOWN',
            # 'EASTHILL',
            # 'DOWNTOWN'
        ]

        with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
            for store in stores: 
                craft_bot.get_all_orders_from_webpage(store, download_pdf=True)
            sort_orders(ORDER_FILES_PATH)
        return
    
    # for vendor in vendors: get_all_orders_from_vendor(driver, vendor)

    # get_all_orders_from_all_stores(driver)

    
    transfer_vendor = 'Ithaca Bakery'
    # format_orders_for_transfer(transfer_vendor, ORDER_FILES_PATH)
    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
    #     for transfer_file in get_transfers(transfer_vendor):

    #         store_to            = transfer_file.split(' _ ')[2].split(' ')[0]
    #         store_from          = 'BAKERY'
    #         items               = []
    #         date_from_file_name = transfer_file.split(' _ ')[2].split(' ')[1].split('.')[0]
    #         month               = int(date_from_file_name[0:2])
    #         day                 = int(date_from_file_name[2:4])
    #         year                = int(date_from_file_name[4:])

    #         workbook = load_workbook(f'{ORDER_FILES_PATH}\\{transfer_vendor}\\{transfer_file}')
    #         sheet = workbook.active

    #         for item_row in sheet.iter_rows():
    #             # print(item_row)
    #             to_transfer, name, quantity = item_row

    #             if not to_transfer: continue
                
    #             items.append(TransferItem(name.value, quantity.value))
            
    #         transfer = Transfer(store_from, store_to, items, datetime(year, month, day))
    #         craft_bot.input_transfer(transfer)


    vendor_to_print = [
        'Renzi',
        'Sysco',
        'Performance Food',
        'US Foods',
        # 'BakeMark',
        # 'Lentz',
        # "Regional Distributors, Inc.",
        # 'Johnston Paper',
        # 'DUTCH VALLEY FOOD DIST',
        # 'Eurocafe Imports',
        # 'Coca-Cola',
        # 'Ithaca Bakery',
        # 'Copper Horse Coffee',
        # 'Hill & Markes',
        # 'Johnston Paper',
        # 'FingerLakes Farms',
        # 'Renzi',
        # 'Sysco',
        # 'Performance Food',
        # 'BJ\'s',
        # 'Copper Horse Coffee',
        # 'Webstaurant',
        # 'UNFI',
    ]
    # printer = Printer()    
    # for vendor in vendor_to_print:
    #     for file in get_files(f'{ORDER_FILES_PATH}\\{vendor}'):
    #         if not file.endswith('pdf'): continue
    #         printer.print_file(f'{ORDER_FILES_PATH}\\{vendor}\\{file}')
    #         time.sleep(6)
        
    # print_schedule_daily(get_day('Saturday'))
    # print_schedule_daily(get_day('Sunday'))
    # print_schedule_daily(get_day('Monday'))
    # print_schedule_daily(get_day('Tuesday'))
    # print_schedule_daily(get_day('Wednesday'))
    # print_schedule_daily(get_day('Thursday'))
    # print_schedule_daily(get_day('Friday'))
    
    # copper_path = f'{ORDER_FILES_PATH}\\Copper Horse Coffee'

    # copper_store_string = f'Copper Horse Coffee _ % 06142024.xlsx'
    

    # copper_bot = CopperHorseBot()
    # copper_bot.combine_orders([f'{copper_path}\\{copper_store_string.replace('%', store)}' for store in stores], copper_path)
    # input('click enter when ready')
    # setup_emails_for_sunday()

   
 
    # ithaca_bot = get_bot('Ithaca Bakery')()
    # ithaca_path = f'{ORDER_FILES_PATH}\\Ithaca Bakery\\'

    # ithaca_store_string = f'Ithaca Bakery _ % 06142024.xlsx'

    # ithaca_bot.combine_orders([f'{ithaca_path}{ithaca_store_string.replace('%', store)}' for store in stores], ithaca_path)
    # milk_orders = tuple([join(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\') if isfile(join(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\', file)) and file.endswith('.pdf')])
    # milk_email = Email(tuple([getenv('HILLCREST_DAIRY_CONTACT_EMAIL')]), 'Hillcrest Dairy Order', 'Please see attached for orders, thank you!', cc=None, attachments=milk_orders)
    # prepare_email_to_send(milk_email)
    # produce_pricing_and_email(None)

    

    
    '''Pricing Sheet Protocol'''
    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)
    # download_pricing_sheets(driver)
    # delete_all_files_without_extension(f'{PRICING_FILES_PATH}\\VendorSheets', '.xlsx')
    generate_pricing_sheets()
    
    vendors = [
        # 'Sysco',
        # 'Performance Food',
        # 'Renzi',
        # 'Cortland Produce Inc.',
        'Russo Produce',
        'Behlog Produce',
    ]
    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)
    # for vendor in vendors:
    #     creds = get_credentials(vendor)
    #     bot = get_bot(vendor)()
    #     # file_name = bot.retrieve_pricing_sheet('IBProduce')
    #     bot.format_vendor_pricing_sheet(f'{PRICING_FILES_PATH}\\VendorSheets\\{bot.name}_IBProduce_2024-06-15.xlsx', f'{PRICING_FILES_PATH}\\{bot.name}_IBProduce_{date.today()}.xlsx', )

    # pricer = PriceComparator()
    # pricer.item_skus_file_path = f'{PRICING_FILES_PATH}\\ItemSkus.xlsx'
    # pricer.compare_prices(f'{PRICING_FILES_PATH}\\Pricing Guides\\IBProduce\\IBProduce 2024-06-15.xlsx')