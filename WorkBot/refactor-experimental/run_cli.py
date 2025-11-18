# ==========================================================
#                        RUN FILE
# ==========================================================
'''
Run file for WorkBot CLI.
Bootstraps repositories, infrastructure, services, bots, and launches the CLI interface.
'''

from backend.app.cli.workbot_cli import WorkBotCLI
from backend.app.ports.repos import Repository
from backend.infra.paths import (
    DOWNLOADS_PATH,
    ORDER_FILES_DIR,
    UPLOAD_FILES_DIR,
    VENDOR_FILES_DIR,
    TRANSFER_FILES_DIR,
    STORE_FILES_DIR,
    ORDER_ARCHIVE_FILES_DIR,
    TRANSFER_ARCHIVE_FILES_DIR,
)
from backend.infra.config.settings import DEFAULT_TRANSFER_ORIGIN

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

def create_repositories() -> dict[str, Repository]:
    '''
    Instantiate file-based repositories for all domain entities.

    Returns:
        A dictionary containing repositories for orders, vendors,
        transfers, and stores.
    '''
    from backend.adapters.repos.order_file_repository import OrderFileRepository
    from backend.adapters.repos.transfer_file_repository import TransferFileRepository
    from backend.adapters.repos.vendor_file_repository import VendorFileRepository
    from backend.adapters.repos.store_file_repository import StoreFileRepository

    orders_repo    = OrderFileRepository(ORDER_FILES_DIR, UPLOAD_FILES_DIR, ORDER_ARCHIVE_FILES_DIR)
    vendors_repo   = VendorFileRepository(VENDOR_FILES_DIR)
    transfers_repo = TransferFileRepository(TRANSFER_FILES_DIR, TRANSFER_ARCHIVE_FILES_DIR)
    stores_repo    = StoreFileRepository(STORE_FILES_DIR)

    return {
        'orders':    orders_repo,
        'vendors':   vendors_repo,
        'transfers': transfers_repo,
        'stores':    stores_repo
    }

def create_infra(repos) -> dict:
    '''
    Build shared infrastructure components.

    Includes:
        - ThreadedDownloadAdapter for concurrent downloads.
        - FileLocator for resolving paths to vendor/store/order files.
    '''
    # from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter
    from backend.adapters.downloads.local_download_manager import LocalDownloadManager
    from backend.app.services.file_locator import FileLocator

    # downloader = ThreadedDownloadAdapter(DOWNLOADS_PATH)
    download_manager = LocalDownloadManager(DOWNLOADS_PATH)
    file_locator = FileLocator(repos['orders'], repos['vendors'], repos['stores'])

    return {
        'downloader': download_manager,
        'locator': file_locator
    }

def create_domain_services(repos, infra) -> dict:
    '''
    Create the core domain services layer.

    Wires together repositories and supporting infrastructure
    for Orders, Vendors, Transfers, and Stores.
    '''
    from backend.app.services.order_service import OrderServices
    from backend.app.services.transfer_service import TransferServices
    from backend.app.services.vendor_service import VendorServices
    from backend.app.services.store_service import StoreServices

    downloader = infra['downloader']

    orders_service    = OrderServices(repos['orders'], downloader)
    vendors_service   = VendorServices(repos['vendors'], downloader)
    transfers_service = TransferServices(repos['transfers'], repos['orders'], DEFAULT_TRANSFER_ORIGIN)
    stores_service    = StoreServices(repos['stores'], downloader)

    return {
        'orders':    orders_service,
        'vendors':   vendors_service,
        'transfers': transfers_service,
        'stores':    stores_service
    }

def create_email_service(services, infra):
    '''
    Initialize the EmailServices layer.

    Connects the emailer provider with domain services
    for automated communication and report delivery.
    '''
    from backend.app.services.email_service import EmailServices
    from backend.adapters.emailer.emailer import Emailer, Email
    from backend.adapters.emailer.registry import EmailProviderRegistry

    provider = EmailProviderRegistry.get('outlook')
    emailer  = Emailer(provider)

    return EmailServices(
        emailer=emailer, 
        orders=services['orders'], vendors=services['vendors'], 
        locator=infra['locator']
    )

def create_craftable_bot(infra):
    '''
    Initialize the CraftableBot for interacting with the Craftable platform.

    Handles login credential retrieval and ties into the OrderService
    for downloading or automating order workflows.
    '''
    from backend.bots.craftable_bot.craftable_bot import CraftableBot
    from backend.bots.craftable_bot.helpers import generate_craftablebot_args
    
    username, password = generate_craftablebot_args()

    return CraftableBot(username, password, infra['downloader'], DOWNLOADS_PATH)   

def create_workbot(services, infra, emailer, craft_bot):
    '''
    Compose the top-level WorkBot controller.

    Aggregates all service layers, automation bots, and email components
    into a single orchestrator used by the CLI.
    '''
    from backend.bots.workbot.work_bot import WorkBot

    return WorkBot(
        services['orders'], services['transfers'], services['vendors'], services['stores'],
        emailer,
        craft_bot,
        infra['downloader']
    )

def create_cli(work_bot):
    return WorkBotCLI(work_bot)

def main() -> None:
    '''Main entry point. Bootstraps all components and starts the CLI.'''

    repos           = create_repositories()
    infra           = create_infra(repos)
    services        = create_domain_services(repos, infra)
    emails_service  = create_email_service(services, infra)
    craft_bot       = create_craftable_bot(infra)
    work_bot        = create_workbot(services, infra, emails_service, craft_bot)

    cli = create_cli(work_bot)
    cli.start(WELCOME_BANNER)

if __name__ == '__main__':
    main()
