from backend.app.cli.workbot_cli import WorkBotCLI
from backend.app.ports.repos import Repository

from backend.infra.paths import (
    DOWNLOADS_PATH,
    ORDER_FILES_DIR,
    UPLOAD_FILES_DIR,
    VENDOR_FILES_DIR,
    TRANSFER_FILES_DIR,
    STORE_FILES_DIR,
    ORDER_ARCHIVE_FILES_DIR
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

WELCOME_BANNER = r'''
    
 ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ████████╗
 ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
 ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██████╔╝██║   ██║   ██║   
 ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║   ██║   
 ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██████╔╝╚██████╔╝   ██║   
  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝   

                  Welcome to WorkBot CLI
            Automate Orders. Eliminate Tedium.
'''

def create_repositories() -> dict[Repository]:

    from backend.adapters.repos.order_file_repository import OrderFileRepository
    from backend.adapters.repos.transfer_file_repository import TransferFileRepository
    from backend.adapters.repos.vendor_file_repository import VendorFileRepository
    from backend.adapters.repos.store_file_repository import StoreFileRepository

    orders_repo    = OrderFileRepository(ORDER_FILES_DIR, UPLOAD_FILES_DIR, ORDER_ARCHIVE_FILES_DIR)
    vendors_repo   = VendorFileRepository(VENDOR_FILES_DIR)
    transfers_repo = TransferFileRepository(TRANSFER_FILES_DIR)
    stores_repo    = StoreFileRepository(STORE_FILES_DIR)

    return {
        'orders': orders_repo,
        'vendors': vendors_repo,
        'transfers': transfers_repo,
        'stores': stores_repo
    }

def create_secondary_infra(repos) -> dict:

    from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter
    from backend.app.services.file_locator import FileLocator

    downloader = ThreadedDownloadAdapter(DOWNLOADS_PATH)
    file_locator = FileLocator(repos['orders'], repos['vendors'], repos['stores'])

    return {
        'downloader': downloader,
        'files': file_locator
    }

def create_domain_services(repos, infra) -> dict:

    from backend.app.services.services_order import OrderServices
    from backend.app.services.services_transfer import TransferServices
    from backend.app.services.services_vendor import VendorServices
    from backend.app.services.services_store import StoreServices

    downloader = infra['downloader']

    orders_service    = OrderServices(repos['orders'], downloader)
    vendors_service   = VendorServices(repos['vendors'], downloader)
    transfers_service = TransferServices(repos['transfers'], repos['orders'], DEFAULT_TRANSFER_ORIGIN)
    stores_service    = StoreServices(repos['stores'], downloader)

    return {
        'orders': orders_service,
        'vendors': vendors_service,
        'transfers': transfers_service,
        'stores': stores_service
    }

def create_email_service(services, infra):

    from backend.app.services.services_emailer import EmailServices
    from backend.adapters.emailer.emailer import Emailer, Email
    from backend.adapters.emailer.registry import EmailProviderRegistry

    provider = EmailProviderRegistry.get("outlook")
    emailer  = Emailer(provider)

    emails_service = EmailServices(emailer=emailer, orders=services['orders'], vendors=services['vendors'], locator=infra['files'])

    return emails_service

def create_craftable_bot(services):

    # driver_options = create_options(downloads_path=DOWNLOADS_PATH)
    # driver = create_driver(driver_options)
    
    from backend.bots.craftable_bot.craftable_bot import CraftableBot
    from backend.bots.craftable_bot.helpers import generate_craftablebot_args
    
    username, password = generate_craftablebot_args()
    craft_bot = CraftableBot(username, password, services['orders'])

    return craft_bot

def create_workbot(services, emailer, craft_bot):

    from backend.bots.workbot.work_bot import WorkBot

    work_bot = WorkBot(
        services['orders'], services['transfers'], services['vendors'], services['stores'],
        emailer,
        craft_bot
    )

    return work_bot

def create_cli(work_bot):
    return WorkBotCLI(work_bot)

def main() -> None:
    
    repos           = create_repositories()
    secondary_infra = create_secondary_infra(repos)
    services        = create_domain_services(repos, secondary_infra)
    emails_service  = create_email_service(services, secondary_infra)
    craft_bot       = create_craftable_bot(services)
    work_bot        = create_workbot(services, emails_service, craft_bot)

    cli = create_cli(work_bot)
    cli.start(WELCOME_BANNER)

if __name__ == '__main__':
    main()
