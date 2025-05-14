from backend.craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc

from dotenv import load_dotenv
from os import getenv
from os import listdir, remove as os_remove, rename
from os.path import isfile, join

from backend.helpers.selenium_helpers import create_driver, create_options

from backend.helpers import  FormatItemData

from openpyxl import load_workbook, Workbook

# from backend.printing.Printer import Printer
from backend.emailer.Emailer import Emailer
from backend.emailer.Services.Service import Email
from backend.emailer.Services.Outlook import OutlookService
from backend.emailer.Services.Gmail import GmailService

# from backend.printing.Printer import Printer
from backend.transferring.TransferManager import TransferManager
from backend.transferring.Transfer import Transfer, TransferItem
from backend.pricing.PriceComparator import PriceComparator
from backend.ordering.OrderManager import OrderManager
from backend.ordering.Order import Order
from backend.vendors.VendorManager import VendorManager


from backend.vendors.vendor_bots.USFoodsBot import USFoodsBot
from datetime import date
import json
from config.paths import VENDORS_DIR
from pathlib import Path
from pprint import pprint

from backend.workbot.WorkBot import WorkBot

dotenv = load_dotenv()

CRAFTABLE_USERNAME = getenv('CRAFTABLE_USERNAME')
CRAFTABLE_PASSWORD = getenv('CRAFTABLE_PASSWORD')

SOURCE_PATH = Path(__file__).parent / 'backend'

ORDER_FILES_PATH   = SOURCE_PATH / 'ordering' / 'OrderFiles'
PRICING_FILES_PATH = SOURCE_PATH / 'pricing'
DOWNLOAD_PATH      = SOURCE_PATH / 'downloads'
TRANSFER_PATH      = SOURCE_PATH / 'transferring'


def get_files(path: str) -> list:
	return [file for file in listdir(path) if isfile(join(path, file))]

def get_excel_files(path: Path) -> list[Path]:
	return [path / file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.xlsx') and '~' not in file]

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

def download_pricing_sheets(driver, vendors=['Sysco', 'Performance Food', 'US Foods', 'Russo Produce',], guides=['IBProduce']) -> None:

    for vendor in vendors:

        vendor_manager = VendorManager()

        bot = vendor_manager.initialize_vendor(vendor, driver)
        # print(bot, flush=True)
        for pricing_guide in guides:

            if vendor not in [
                 'US Foods', 
                #  'Sysco', 
                #  'Performance Food'
                ]:
                file_name = bot.retrieve_pricing_sheet(pricing_guide)
                # file_name = None
                new_file_name = PRICING_FILES_PATH / 'VendorSheets' / f'{bot.name}_{pricing_guide}_{date.today()}.{file_name.split(".")[1]}'

            elif vendor == 'US Foods':
                file_name = 'US Foods_IBProduce.csv'
                new_file_name = PRICING_FILES_PATH / 'VendorSheets' / 'US Foods_IBProduce_2025-05-11.csv'
            
            # elif vendor == 'Sysco':
            #     file_name = 'Sysco_IBProduce.csv'
            #     new_file_name = PRICING_FILES_PATH / 'VendorSheets' / 'Sysco_IBProduce_2025-03-23.csv'
            
            # elif vendor == 'Performance Food':
            #     file_name = 'Performance Food_IBProduce.xlsx'
            #     new_file_name = PRICING_FILES_PATH / 'VendorSheets' / 'Performance Food_IBProduce_2025-03-23.xlsx'

            # new_file_name = PRICING_FILES_PATH / 'VendorSheets' / f'{bot.name}_{pricing_guide}_{date.today()}.{file_name.split(".")[1]}'

            
            # new_file_name = PRICING_FILES_PATH / 'VendorSheets' / 'US Foods_IBProduce_2025-03-10.csv'
            rename( DOWNLOAD_PATH / file_name, new_file_name)
            bot.format_vendor_pricing_sheet(new_file_name, new_file_name.with_suffix('.xlsx'))
        
    return

def generate_pricing_sheets(vendors=['Sysco', 'Performance Food', 'US Foods', 'Russo Produce',], guides=['IBProduce']):
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


if __name__ == '__main__':

    vendors = [ 
        # 'Sysco', 
        # 'Performance Food',
        # 'US Foods',
        # 'Renzi',
        'UNFI',
        # 'Hill & Markes',
        # 'Johnston Paper',
        # 'Regional Distributors, Inc.',
        # 'Peters Supply',
        # 'SANICO',
        # 'Copper Horse Coffee',
        # 'Equal Exchange',
        # 'Eurocafe Imports',
        # 'Macro Mamas',
        # 'Coca-Cola',
        # 'FingerLakes Farms',
        # 'Ithaca Bakery',
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
        # 'Russo Produce',
        # 'BEHLOG & SON, INC.',
    ]

    stores = [
        #  'BAKERY',
         'TRIPHAMMER',
         'COLLEGETOWN',
         'EASTHILL',
         'DOWNTOWN'
    ]
    
    
    # gmail_service = GmailService()

    # emailer = Emailer(gmail_service)

    # test_email = Email(
    #     to=('andrew.ctb.ithaca@gmail.com',),
    #     subject='Test Email',
    #     body='This is a test email for the automated service.'
    # )

    # test_email_data = gmail_service.create_email(test_email)
    # gmail_service.display_email(test_email_data)

    # input('Press Enter to send email')
    # gmail_service.send_email(test_email_data)


   


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
        



    


    


    

    
    '''Pricing Sheet Protocol'''
    # options = create_options(DOWNLOAD_PATH)
    # driver  = uc.Chrome(options=options, use_subprocess=True)
    # download_pricing_sheets(driver)
    # delete_all_files_without_extension(PRICING_FILES_PATH / 'VendorSheets', '.xlsx')
    # input('Press ENTER to stop waiting.')
    # generate_pricing_sheets()
    



    # NEED A WHITELIST OF ITEMS OTHERWISE ALL ~2500 ITEMS WILL BE LISTED
    # ANSWER: Use the par list and count only those items with a par above 0.
    # Use the OrderForm Excel file, it has the pars and ordered amount baked in.



    
    #{
    #   item_name: {store_name: {onhand: qty, par: par, ordered: 0}, store_name: quantity}
    #}

    def load_item_counts(files: list) -> dict:

        item_counts = {}
        filename_store_map = {
            'East Hill Plaza': 'Easthill',
            'Syracuse':        'Syracuse',
            'College Ave':     'Collegetown',
            'Triphammer Rd':   'Triphammer',
            'State St':        'Downtown'
        }

        for filename in filename_store_map:
            
            orderform_path = [i for i in files if filename in i.name][0]
        
            orderform_workbook = load_workbook(orderform_path)
            orderform_sheet = orderform_workbook.active

            store_name = filename_store_map[filename]

            for row in orderform_sheet.iter_rows(min_row=6):
                item_par = row[2].value
                if item_par <= 0: continue
                 
                item_name  = row[1].value
                order_qty  = row[5].value
                onhand_qty = row[3].value
                
                if item_name not in item_counts:
                    item_counts[item_name] = {store_name: {'onhand': onhand_qty, 'par': item_par, 'ordered': order_qty}}
                else:
                    if store_name not in item_counts[item_name]:
                        item_counts[item_name][store_name] = {'onhand': onhand_qty, 'par': item_par, 'ordered': order_qty}
        
        return item_counts
    # pprint(item_counts)

    def item_counts_to_excel_workbook(item_counts) -> Workbook:

        comparison_workbook = Workbook()
        sheet = comparison_workbook.active
        stores = []
        store_col_offset = 3
        for pos, item in enumerate(item_counts):
            item_name = item.split(' ')
            item_unit = item_name[-1]
            item_name = ' '.join(item_name[:-1])

            item_info = item_counts[item]
            sheet.cell(row=pos+2, column=1).value = item_name
            sheet.cell(row=pos+2, column=2).value = item_unit
            for store in item_info:
                onhand  = item_info[store]['onhand']
                ordered = item_info[store]['ordered']
                par     = item_info[store]['par']

                if store not in stores: stores.append(store)
                store_index = stores.index(store)

                store_col_pos = (store_index+1) * store_col_offset
                sheet.cell(row=1, column=store_col_pos).value = store
                sheet.cell(row=pos+2, column=store_col_pos).value = onhand
                sheet.cell(row=pos+2, column=store_col_pos+1).value = par
                sheet.cell(row=pos+2, column=store_col_pos+2).value = ordered

        return comparison_workbook


    dir_path = DOWNLOAD_PATH / 'testing'
    orderform_file_paths = [i for i in dir_path.iterdir() if i.is_file() and 'Order Form' in i.name]

    item_counts = load_item_counts(orderform_file_paths)
    item_count_workbook = item_counts_to_excel_workbook(item_counts)
    item_count_workbook.save('testing.xlsx')


            


            

        # 1. Open audit
        # 2. Extract necessary item counts
            # a. Name: Col2, Unit Count: Col4, Total Count: Col-3
        # 3. Update combine sheet
            # a. Use order combine function?
        # 4. Close audit

