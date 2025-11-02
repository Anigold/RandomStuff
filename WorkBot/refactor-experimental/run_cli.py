from backend.app.cli.workbot_cli import WorkBotCLI

from backend.infra.paths import (
    DOWNLOADS_PATH,
    ORDER_FILES_DIR,
    UPLOAD_FILES_DIR,
    VENDOR_FILES_DIR,
    TRANSFER_FILES_DIR,
    STORE_FILES_DIR
)

from backend.infra.config.settings import DEFAULT_TRANSFER_ORIGIN

import undetected_chromedriver as uc

def create_options(downloads_path) -> uc.ChromeOptions:

    options = uc.ChromeOptions()
    preferences = {
        'plugins.plugins_list':               [{'enabled': False, 'name': 'Chrome PDF Viewer'}],
        'download.default_directory':         str(downloads_path), # Needs to be casted to a string for proper Chrome Driver handling.
        'download.prompt_for_download':       False,
        'safebrowsing.enabled':               True,
        'plugins.always_open_pdf_externally': True,
        'download.directory_upgrade':         True,
    }
    options.add_experimental_option('prefs', preferences)
    
    return options

def create_driver(options):
    return uc.Chrome(options=options, use_subprocess=True)

if __name__ == '__main__':

    # ------------------------------------------
    # Data Repository Settings
    # ------------------------------------------
    from backend.adapters.repos.order_file_repository import OrderFileRepository
    from backend.adapters.repos.transfer_file_repository import TransferFileRepository
    from backend.adapters.repos.vendor_file_repository import VendorFileRepository
    from backend.adapters.repos.store_file_repository import StoreFileRepository
    
    from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter
    from backend.app.services.file_locator import FileLocator

    orders_repo    = OrderFileRepository(ORDER_FILES_DIR, UPLOAD_FILES_DIR)
    vendors_repo   = VendorFileRepository(VENDOR_FILES_DIR)
    transfers_repo = TransferFileRepository(TRANSFER_FILES_DIR)
    stores_repo    = StoreFileRepository(STORE_FILES_DIR)

    downloader     = ThreadedDownloadAdapter(DOWNLOADS_PATH)
    file_locator   = FileLocator(orders_repo, vendors_repo, stores_repo)

    # ------------------------------------------
    # Domain Services Settings
    # ------------------------------------------
    from backend.app.services.services_order import OrderServices
    from backend.app.services.services_transfer import TransferServices
    from backend.app.services.services_vendor import VendorServices
    from backend.app.services.services_store import StoreServices

    orders_service    = OrderServices(orders_repo, downloader)
    vendors_service   = VendorServices(vendors_repo, downloader)
    transfers_service = TransferServices(transfers_repo, orders_repo, DEFAULT_TRANSFER_ORIGIN)
    stores_service    = StoreServices(stores_repo, downloader)

    # ------------------------------------------
    # Secondary Services Settings
    # ------------------------------------------
    from backend.app.services.services_emailer import EmailServices
    from backend.adapters.emailer.emailer import Emailer, Email
    from backend.adapters.emailer.registry import EmailProviderRegistry

    provider = EmailProviderRegistry.get("outlook")
    emailer  = Emailer(provider)

    emails_service = EmailServices(emailer=emailer, orders=orders_service, vendors=vendors_service, locator=file_locator)

    # ------------------------------------------
    # CraftableBot Automation Settings
    # ------------------------------------------
    driver_options = create_options(downloads_path=DOWNLOADS_PATH)
    driver = create_driver(driver_options)
    
    from backend.bots.craftable_bot.craftable_bot import CraftableBot
    from backend.bots.craftable_bot.helpers import generate_craftablebot_args
    
    username, password = generate_craftablebot_args()
    craft_bot = CraftableBot(username, password, orders_service)

    # ------------------------------------------
    # WorkBot Settings
    # ------------------------------------------
    from backend.bots.workbot.work_bot import WorkBot

    work_bot = WorkBot(
        orders_service, transfers_service, vendors_service, stores_service,
        emails_service,
        craft_bot
    )

    # ------------------------------------------
    # CLI Settings
    # ------------------------------------------

    workbot_cli = WorkBotCLI(work_bot)
    welcome_screen = rf'''
    
 ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ████████╗
 ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
 ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██████╔╝██║   ██║   ██║   
 ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║   ██║   
 ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██████╔╝╚██████╔╝   ██║   
  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   

                  Welcome to WorkBot CLI
            Automate Orders. Eliminate Tedium.

{work_bot.welcome_to_work()}
'''
    # ------------------------------------------
    # RUN
    # ------------------------------------------
    workbot_cli.start(welcome_screen)
