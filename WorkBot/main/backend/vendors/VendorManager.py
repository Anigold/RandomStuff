import logging
import importlib
from backend.vendors.vendor_config import get_vendor_information, get_vendor_credentials
from backend.helpers.selenium_helpers import create_driver, create_options
from pathlib import Path
from backend.logger.Logger import Logger

SOURCE_PATH         = Path(__file__).parent.parent
ORDERS_DIRECTORY    = SOURCE_PATH / 'orders' / 'OrderFiles'
DOWNLOADS_DIRECTORY = SOURCE_PATH / 'downloads'

@Logger.attach_logger
class VendorManager:
    '''Dynamically manages vendor bot instances.'''
    
    def __init__(self):
        self.active_vendors = {} 

    def initialize_vendor(self, vendor_name, driver=None):
        '''Creates and stores a vendor bot instance.'''

        if vendor_name in self.active_vendors:
            self.logger.info(f'{vendor_name} bot is already initialized.')
            return self.active_vendors[vendor_name]

        vendor_info         = self._load_vendor_info(vendor_name)
        vendor_bot_class    = self._load_vendor_class(vendor_info)
        vendor_bot_instance = self._instantiate_vendor_bot(vendor_bot_class, vendor_name, vendor_info, driver)
        
        self.active_vendors[vendor_name] = vendor_bot_instance
        self.logger.info(f'Initialized {vendor_name} bot.')
        return vendor_bot_instance

    def _load_vendor_info(self, vendor_name: str) -> dict:
        '''Fetches vendor configuration information.'''
        vendor_info = get_vendor_information(vendor_name)
        if not vendor_info:
            raise ValueError(f'No vendor configuration found for {vendor_name}')
        return vendor_info
    
    def _load_vendor_class(self, vendor_info: dict):
        try:
            module = importlib.import_module(vendor_info['module_path'])
            return getattr(module, vendor_info['bot_class'])
        except (ImportError, AttributeError) as e:
            raise ImportError(f'Could not load {vendor_info['bot_class']} from {vendor_info['module_path']}: {e}')

    def _instantiate_vendor_bot(self, bot_class, vendor_name, vendor_info, driver):
        '''Instantiate vendor bot instance with necessary dependencies.'''

        init_args, init_kwargs = [], {}

        if vendor_info.get('uses_selenium', False):
            driver = driver or create_driver(create_options(DOWNLOADS_DIRECTORY))              
            init_args.append(driver)

        if vendor_info.get('requires_credentials', False):
            credentials = get_vendor_credentials(vendor_name)
            init_kwargs.update({
                'username': credentials['username'],
                'password': credentials['password']
            })
            
        return bot_class(*init_args, **init_kwargs)

    def get_active_vendor(self, vendor_name):
        '''Retrieves an already initialized vendor instance.'''
        return self.active_vendors.get(vendor_name)

    def close_all_vendors(self):
        '''Logs out and closes all active vendor sessions.'''
        for vendor, bot in self.active_vendors.items():
            if hasattr(bot, "logout"):
                bot.logout()
            self.logger.info(f'Closed session for {vendor}.')
        self.active_vendors.clear()

    def close_vendor(self, vendor_name):
        '''Logs out and removes a specific vendor instance.'''
        bot = self.active_vendors.get(vendor_name)
        if bot and hasattr(bot, 'logout'):
            bot.logout()
        self.active_vendors.pop(vendor_name, None)
        self.logger.info(f'Closed session for {vendor_name}.')

    def get_vendor_information(self, vendor_name: str) -> dict:
        return get_vendor_information(vendor_name)
    