from backend.craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc

from dotenv import load_dotenv
from os import getenv
from os import listdir, remove as os_remove, mkdir, rename
from os.path import isfile, join, isdir
import os

from backend.helpers import  FormatItemData

from backend.vendor_bots.VendorBot import VendorBot
from backend.vendor_bots.HillNMarkesBot import HillNMarkesBot
from backend.vendor_bots.USFoodsBot import USFoodsBot
from backend.vendor_bots.CopperHorseBot import CopperHorseBot
from backend.vendor_bots.PerformanceFoodBot import PerformanceFoodBot
from backend.vendor_bots.SyscoBot import SyscoBot
from backend.vendor_bots.UNFIBot import UNFIBot
from backend.vendor_bots.IthacaBakeryBot import IthacaBakeryBot
from backend.vendor_bots.DutchValleyBot import DutchValleyBot
from backend.vendor_bots.CortlandProduceBot import CortlandProduceBot
from backend.vendor_bots.BehlogProduceBot import BehlogProduceBot
from backend.vendor_bots.RussoProduceBot import RussoProduceBot
from backend.vendor_bots.EuroCafeBot import EuroCafeBot

from backend.orders.OrderManager import OrderManager
from backend.orders.OrderBot import OrderBot

from backend.stores.Store import Store
from backend.stores.StoreManager import StoreManager

from backend.emailer.Emailer import Emailer
from backend.emailer.Services.Service import Email
from backend.emailer.Services.Outlook import Outlook

from backend.printing.Printer import Printer
from backend.transferring.TransferManager import TransferManager
from backend.transferring.Transfer import Transfer, TransferItem
from backend.pricing.PriceComparator import PriceComparator

from backend.smallwares.WebstaurantBot import WebstaurantBot

from datetime import date, datetime

from openpyxl import load_workbook

from pathlib import Path

dotenv = load_dotenv()

CRAFTABLE_USERNAME = getenv('CRAFTABLE_USERNAME')
CRAFTABLE_PASSWORD = getenv('CRAFTABLE_PASSWORD')

SOURCE_PATH = Path(__file__).parent / 'backend'

ORDER_FILES_PATH   = SOURCE_PATH / 'orders' / 'OrderFiles'
PRICING_FILES_PATH = SOURCE_PATH / 'pricing'
DOWNLOAD_PATH      = SOURCE_PATH / 'downloads'
TRANSFER_PATH      = SOURCE_PATH / 'transferring'

def get_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file))]

# def sort_orders(path: str, override=True) -> None:
#     # Sort and group orders
#     files = get_files(path)
#     for file in files:
        
#         vendor_name = file.split('_')[0].strip()

#         if not isdir(f'{path}\\{vendor_name}'):
#             mkdir(f'{path}\\{vendor_name}')
        
#         rename(f'{path}\\{file}', f'{path}\\{vendor_name}\\{file}')
#     return

def create_options() -> uc.ChromeOptions:

    options = uc.ChromeOptions()
    preferences = {
        "plugins.plugins_list":               [{"enabled": False, "name": "Chrome PDF Viewer"}],
        "download.default_directory":         str(DOWNLOAD_PATH), # Needs to be casted to a string for proper Chrome Driver handling.
        "download.prompt_for_download":       False,
        "safebrowsing.enabled":               True,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade":         True,
    }
    options.add_experimental_option("prefs", preferences)
    
    return options

def get_store(name: str) -> Store:
    store_manager = StoreManager(storage_file=SOURCE_PATH / 'stores' / 'stores.json')
    return store_manager.find_store_by_name(name)

def get_credentials(name) -> dict:

    username = getenv(f'{name.upper().replace(" ", "_")}_USERNAME') or None
    password = getenv(f'{name.upper().replace(" ", "_")}_PASSWORD') or None

    return {'username': username, 'password': password}

def get_bot(name) -> VendorBot:
     
    bots = {
        'US Foods': USFoodsBot,
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
        'Webstaurant': WebstaurantBot,
        'Eurocafe Imports': EuroCafeBot,
    }

    if name not in bots:
        return
    
    return bots[name]

def check_bot_if_creds_are_needed(name) -> bool:
    bots = {
        'Renzi': True,
        'Hill & Markes': True,
        'Sysco': True,
        'Performance Food': True,
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

'''FIX THIS UGLY-ASS HACKY JOB'''
def format_orders(vendor: str, path_to_folder: str) -> None:
    vendor_bot  = get_bot(vendor)()
    excel_files = get_excel_files(path_to_folder / vendor_bot.name)
    for file in excel_files:
        file_name_no_extension  = file.name.split('.')[0]
        item_data               = FormatItemData.extract_item_data_from_excel_file(f'{file}')
        vendor_bot.format_for_file_upload(item_data, f'{path_to_folder}\\{vendor_bot.name}\\Formatted _ {file_name_no_extension}')
    return

def format_orders_for_transfer(vendor: str, path_to_folder: str) -> None:
    vendor_bot  = get_bot(vendor)()
    excel_files = get_excel_files(path_to_folder / vendor)
    for file in excel_files:
        file_name_no_extension = file.name.split('.')[0]
        item_data = FormatItemData.extract_item_data_from_excel_file_for_transfer(path_to_folder / vendor_bot.name / file)
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
    # euro_cafe_order_attachments             = tuple([join(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\') if isfile(join(f'{ORDER_FILES_PATH}\\Eurocafe Imports\\', file)) and file.endswith('.pdf')])
    # macro_mamas_order_attachments           = tuple([join(f'{ORDER_FILES_PATH}\\Macro Mamas\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Macro Mamas\\') if isfile(join(f'{ORDER_FILES_PATH}\\Macro Mamas\\', file)) and file.endswith('.pdf')])
    
    sunday_emailer = Emailer(service=Outlook)

    emails = [
        {
        'subject': 'Equal Exchange Order',
        'to': ['orders@equalexchange.coop'],
        'body': 'Please see attached for orders, thank you!',
        'attachments': equal_exchange_order_attachments
        },
        # {
        # 'subject': 'Euro Cafe Order',
        # 'to': ['sales@eurocafeimports.com'],
        # 'body': 'Please see attached for orders, thank you!',
        # 'cc': 'scott.tota@eurocafeimports.com',
        # 'attachments': euro_cafe_order_attachments
        # },
        {
        'subject': 'Fingerlakes Farms Order',
        'to': ['orders@ilovenyfarms.com'],
        'body': 'Please see attached for orders, thank you!',
        'attachments': finger_lakes_farms_order_attachments
        },
        # {
        # 'subject': 'Macro Mama Order',
        # 'to': ['macromamas@gmail.com'],
        # 'body': 'Please see attached for orders, thank you!',
        # 'attachments': macro_mamas_order_attachments
        # },
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
            new_file_name = f'{PRICING_FILES_PATH}{bot.name} {pricing_guide} {date.today()}.{file_name.split(".")[-1]}'

            rename(f'{DOWNLOAD_PATH}{file_name}', new_file_name)

    emailer             = Emailer(service=Outlook)
    recipients          = ('kitchen.ibctb@gmail.com', 'milesbrous@gmail.com', 'mimimehaffey@gmail.com')
    produce_sheet_path  = tuple([join(f'{PRICING_FILES_PATH}', 'ProducePricing.xlsx')])
    email               = Email(recipients, 'Produce Pricing', '', cc=None, attachments=produce_sheet_path)

    emailer.create_email(email)
    emailer.display_email(email)
    return

def download_pricing_sheets(driver, vendors=['Sysco', 'Performance Food', 'US Foods', 'Behlog Produce', 'Russo Produce',], guides=['IBProduce']) -> None:

    for vendor in vendors:
        creds = get_credentials(vendor)
        bot = get_bot(vendor)() if creds['username'] == None else get_bot(vendor)(driver, creds['username'], creds['password'])

        for pricing_guide in guides:
            file_name = bot.retrieve_pricing_sheet(pricing_guide)
    
            new_file_name = f'{PRICING_FILES_PATH}\\VendorSheets\\{bot.name}_{pricing_guide}_{date.today()}.{file_name.split(".")[1]}'

            rename(f'{DOWNLOAD_PATH}\\{file_name}', new_file_name)
            # print(new_file_name)
            bot.format_vendor_pricing_sheet(new_file_name, f'{new_file_name.rsplit(".", 1)[0]}.xlsx')
        
    return

def generate_pricing_sheets(vendors=['Sysco', 'Performance Food', 'US Foods', 'Behlog Produce', 'Russo Produce',], guides=['IBProduce']):
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

def generate_weekly_orders_email(store: str, to: list):

    order_paths_by_store = get_pdfs_by_store(ORDER_FILES_PATH, store)
    # pprint.pprint(order_paths_by_store)
    emailer = Emailer(service=Outlook)

    store_orders_path = order_paths_by_store[store]
    email = Email(
        tuple(to), 
        'Weekly Orders', 
        '',
        attachments=tuple(store_orders_path)
    )
    
    emailer.create_email(email)
    emailer.display_email(email)
    return 

def delete_orders_from_craftable(stores: list[str]) -> None:

    options = create_options()
    driver  = uc.Chrome(options=options, use_subprocess=True)

    with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
        for store in stores: craft_bot.delete_all_orders(store)

    return

if __name__ == '__main__':

    vendors = [ 
        'Sysco', 
        'Performance Food',
        'US Foods',
        # 'Renzi',
        'UNFI',
        # 'Hill & Markes',
        # 'Johnston Paper',
        # 'Regional Distributors, Inc.',
        # 'Peters Supply',
        # 'SANICO',
        # 'Copper Horse Coffee',
        # 'Equal Exchange',
        'Eurocafe Imports',
        # 'Macro Mamas',
        # 'Coca-Cola',
        # 'FingerLakes Farms',
        'Ithaca Bakery',
        # 'Webstaurant',
        # 'Hillcrest Dairy',
        # 'Hillcrest Foods',
        # 'BakeMark',
        # 'Lentz',
        # 'Keck\'s Food Service',
        # 'Dawn',
        # 'Cortland Produce Inc.',
        # 'A.L. George',
        # 'BALKAN BEVERAGE LLC',
        # 'Casa',
        # 'Palmer',
        # 'ACE ENDICO',
        'Russo Produce',
        'BEHLOG & SON, INC.',
    ]

    stores = [
         'BAKERY',
         'TRIPHAMMER',
         'COLLEGETOWN',
        #  'EASTHILL',
        #  'DOWNTOWN'
    ]
    

    ''' CURRENT PROJECT: STORE AND ORDER MANAGERS '''
    # store_manager = StoreManager(
    #     storage_file=f'{SOURCE_PATH}\\backend\\stores\\stores.json'
    #     )
    
    # for i in store_manager.stores:
    #     print(i)

    # store_manager.add_store("006", "NEW TEST STORE")
    # store_manager.save_stores()

    # print(store_manager.list_stores())

    # order_manager = OrderManager()
    # order_bot = OrderBot(order_manager)
    
    

    ''' Welcome to Work Protocol '''
    def welcome_to_work() -> None:

        days_of_the_week = [
            'Saturday',
            'Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday'
        ]
        for day in days_of_the_week: print_schedule_daily(get_day(day))

        options = create_options()
        driver  = uc.Chrome(options=options, use_subprocess=True)

        stores = [
            'TRIPHAMMER',
            'COLLEGETOWN',
            'EASTHILL',
            'DOWNTOWN'
        ]


        with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
            for store in stores:
                craft_bot.get_all_orders_from_webpage(store, download_pdf=True, update=False)
        craft_bot.order_manager.sort_orders()

        store_weekly_emails = {
            'DOWNTOWN': ['tucker.coburn@gmail.com', 'hselsner@gmail.com'],
            # 'COLLEGETOWN': ['goldsmithnandrew@gmail.com'],
        }

        for store in store_weekly_emails: generate_weekly_orders_email(store, store_weekly_emails[store])

        return

    # welcome_to_work()
    '''--------------------------'''


    ''' DELETE ORDERS FROM CRAFTABLE '''
    # delete_orders_from_craftable(stores)
    '''------------------------------'''


    ''' DOWNLOAD ORDERS FROM CRAFTABLE '''
    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)

    # update       = True
    # download_pdf = True

    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
    #     craft_bot.download_orders(
    #         stores, 
    #         vendors=vendors, 
    #         download_pdf=download_pdf, 
    #         update=update
    #     )
    #     craft_bot.order_manager.sort_orders()
    '''--------------------------------'''

    ''' TRANSFER ITEMS BETWEEN STORES '''

    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)

    # transfer_manager = TransferManager()
    # transfers_directory = TransferManager.get_transfer_files_directory()

    # test_transfer = transfer_manager.load_transfer_from_file(transfers_directory / 'BAKERY to TRIPHAMMER 20250211.xlsx')

    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
    #     craft_bot.input_transfer(test_transfer)

    '''-------------------------------'''

    ''' FORMAT ORDERS FOR VENDOR UPLOAD '''
    # # sort_orders(ORDER_FILES_PATH)
    for vendor in vendors:
        format_orders(vendor, ORDER_FILES_PATH)
    '''---------------------------------'''

    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)
    
    # transfer_vendor = 'Ithaca Bakery'
    # transfer_files_directory = get_excel_files(ORDER_FILES_PATH / 'Ithaca Bakery')
    # format_orders_for_transfer(transfer_vendor, ORDER_FILES_PATH)
    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
        
    #     print('\nRetrieving transfer files.', flush=True)
    #     for transfer_file in get_transfers(transfer_vendor):

    #         store_to            = transfer_file.split(' _ ')[2].split(' ')[0]
    #         store_from          = 'BAKERY'
    #         items               = []
    #         date_from_file_name = transfer_file.split(' _ ')[2].split(' ')[1].split('.')[0]
    #         year                = int(date_from_file_name[0:4])
    #         month               = int(date_from_file_name[4:6])
    #         day                 = int(date_from_file_name[6:])

    #         print(f'\nCreating transfer for {store_to} on {month}/{day}/{year}.', flush=True)
    #         workbook = load_workbook(ORDER_FILES_PATH / transfer_vendor / transfer_file)
    #         sheet = workbook.active

    #         for item_row in sheet.iter_rows():
    #             # print(item_row)
    #             to_transfer, name, quantity = item_row
    #             print((to_transfer.value, name.value, quantity.value))
    #             if quantity.value < 1: continue

    #             if not to_transfer: continue
                
    #             items.append(TransferItem(name.value, quantity.value))
            
    #         transfer = Transfer(store_from, store_to, items, datetime(year, month, day))
    #         craft_bot.input_transfer(transfer)
    #         workbook.save(f'{ORDER_FILES_PATH}\\{transfer_vendor}\\COMPLETED {transfer_file}')

            # rename(f'{ORDER_FILES_PATH}\\{transfer_vendor}\\{transfer_file}', f'{ORDER_FILES_PATH}\\{transfer_vendor}\\COMPLETED {transfer_file}')

    # with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
        
    #     # transfer_file = ORDER_FILES_PATH / 'Ithaca Bakery' / 'Ithaca Bakery _ TRIPHAMMER 20250211.xlsx'
   
    #     store_to            = transfer_file.split(' _ ')[2].split(' ')[0]
    #     store_from          = 'BAKERY'
    #     items               = []
    #     date_from_file_name = transfer_file.split(' _ ')[2].split(' ')[1].split('.')[0]
    #     year                = int(date_from_file_name[0:4])
    #     month               = int(date_from_file_name[4:6])
    #     day                 = int(date_from_file_name[6:])

    #     print(f'\nCreating transfer for {store_to} on {month}/{day}/{year}.', flush=True)
    #     workbook = load_workbook(ORDER_FILES_PATH / transfer_vendor / transfer_file)
    #     sheet = workbook.active

    #     for item_row in sheet.iter_rows():
    #         # print(item_row)
    #         to_transfer, name, quantity = item_row
    #         print((to_transfer.value, name.value, quantity.value))
    #         if quantity.value < 1: continue

    #         if not to_transfer: continue
            
    #         items.append(TransferItem(name.value, quantity.value))
        
    #     transfer = Transfer(store_from, store_to, items, datetime(year, month, day))
    #     craft_bot.input_transfer(transfer)
    #     workbook.save(f'{ORDER_FILES_PATH}\\{transfer_vendor}\\COMPLETED {transfer_file}')

    def upload_store_transfers(transfer_files: list[Path], origin_store: Store) -> None:

        options = create_options()
        driver  = uc.Chrome(options=options, use_subprocess=True)
        print(origin_store)
        with CraftableBot(driver, CRAFTABLE_USERNAME, CRAFTABLE_PASSWORD) as craft_bot:
            # print("START", flush=True)
            for transfer_file in transfer_files:
                file_name           = transfer_file.name
                store_to            = str(file_name).split(' _ ')[1].split(' ')[0]
                store_from          = origin_store.name
                items               = []
                date_from_file_name = str(file_name).split(' _ ')[1].split(' ')[1].split('.')[0]
                month               = int(date_from_file_name[0:2])
                day                 = int(date_from_file_name[2:4])
                year                = int(date_from_file_name[4:])

                print(f'\nPreparing transfer data between {store_from} to {store_to}.', flush=True)

                workbook = load_workbook(transfer_file)
                sheet = workbook.active

                for item_row in sheet.iter_rows():
                    # print(item_row)
                    name     = item_row[1].value
                    quantity = item_row[2].value
                    # print([name, quantity], flush=True)

                    items.append(TransferItem(name, quantity))
                
                transfer = Transfer(store_from, store_to, items, datetime(year, month, day))
                print(transfer)
                craft_bot.input_transfer(transfer)


    # ithaca_bakery_transfer_files = get_excel_files(ORDER_FILES_PATH / 'Ithaca Bakery')
    # store = get_store('Bakery')
    # print(store)
    # upload_store_transfers(ithaca_bakery_transfer_files, get_store('Bakery'))


    vendor_to_print = [
        'Sysco',
        'Performance Food',
        'US Foods',
        'Renzi',
        # 'BakeMark',
        # 'Lentz',
        # 'Hill & Markes',
        # 'Johnston Paper',
        # 'Regional Distributors, Inc.',
        # 'Peters Supply',
        # 'SANICO',
        # 'DUTCH VALLEY FOOD DIST',
        # 'Eurocafe Imports',
        # 'Coca-Cola',
        # 'FingerLakes Farms',
        # 'Equal Exchange',
        # 'Copper Horse Coffee',
        # 'Webstaurant',
        # 'UNFI',
        'Ithaca Bakery',
    ]
    # printer = Printer()    
    # for vendor in vendor_to_print:
    #     for file in get_files(f'{ORDER_FILES_PATH}\\{vendor}'):
    #         if not file.endswith('pdf'): continue
    #         printer.print_file(f'{ORDER_FILES_PATH}\\{vendor}\\{file}')
    #         time.sleep(6)
        


    

    vendors = [
        # 'Copper Horse Coffee',
        # 'Eurocafe Imports',
        'Ithaca Bakery'
    ]
    # for vendor in vendors:

    #     vendor_bot    = get_bot(vendor)()
    #     vendor_path   = f'{ORDER_FILES_PATH}\\{vendor_bot.name}'
    #     vendor_orders = [join(f'{vendor_path}\\', file) for file in listdir(f'{vendor_path}\\') if isfile(join(f'{vendor_path}\\', file)) and file.endswith('.xlsx')]
    #     # pprint.pprint(vendor_orders)
    #     vendor_bot.combine_orders(vendor_orders, vendor_path)

    
    # input('click enter when ready')
    # setup_emails_for_sunday()



    
    # milk_orders = tuple([join(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\', file) for file in listdir(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\') if isfile(join(f'{ORDER_FILES_PATH}\\Hillcrest Dairy\\', file)) and file.endswith('.pdf')])
    # milk_email = Email(tuple([getenv('HILLCREST_DAIRY_CONTACT_EMAIL')]), 'Hillcrest Dairy Order', 'Please see attached for orders, thank you!', cc=None, attachments=milk_orders)
    # prepare_email_to_send(milk_email)
    # produce_pricing_and_email(None)

    

    
    '''Pricing Sheet Protocol'''
    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)
    # download_pricing_sheets(driver)
    # delete_all_files_without_extension(f'{PRICING_FILES_PATH}\\VendorSheets', '.xlsx')
    # generate_pricing_sheets()
    
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

    # options = create_options()
    # driver  = uc.Chrome(options=options, use_subprocess=True)

    # bot_name = 'Webstaurant'
    # webstaurant_bot_creds = get_credentials(bot_name)
    # webstaurant_bot       = get_bot(bot_name)(driver, webstaurant_bot_creds['username'], webstaurant_bot_creds['password'])

    # order_info = webstaurant_bot.get_order_info(99178108)
    # pprint.pprint(order_info)
    # undocumented_orders = webstaurant_bot.get_all_undocumented_orders()
    # print(undocumented_orders)
    # for order in undocumented_orders:
    #     order_info = webstaurant_bot.get_order_info(order, download_invoice=True)
    #     webstaurant_bot.update_pick_list(order_info)


