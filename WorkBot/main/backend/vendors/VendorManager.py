
import importlib
# from backend.vendors.vendor_config import get_vendor_information, get_vendor_credentials
from backend.helpers.selenium_helpers import create_driver, create_options
from backend.logger.Logger import Logger

from config.paths import DOWNLOADS_DIR, VENDORS_DIR
# from .vendor_config import get_vendors
import json, re
from backend.config import get_env_variable

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

VENDORS       = load_json(VENDORS_DIR / 'vendors.json')["vendors"]
VENDOR_GROUPS = load_json(VENDORS_DIR / 'vendor_groups.json')

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
        vendor_info = self.get_vendor_information(vendor_name)
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
            driver = driver or create_driver(create_options(DOWNLOADS_DIR))              
            init_args.append(driver)

        if vendor_info.get('requires_credentials', False):
            credentials = self._get_vendor_credentials(vendor_name)
            init_kwargs.update({
                'username': credentials['username'],
                'password': credentials['password']
            })
        
        if vendor_info.get('requires_otp', False):
            otp_module = importlib.import_module(vendor_info['module_path'])
            provider = getattr(otp_module, f'{vendor_info['bot_class'][0:-3]}OTPProvider')
            init_kwargs.update({
                'otp_provider': provider
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
        self.logger.info(f'Getting information for: {vendor_name}')
        vendor_info = VENDORS.get(vendor_name, {})
        self.logger.info(f'Information found.')
        self.logger.debug(f'{vendor_info}')
        return vendor_info
    
    def list_vendors(self, group_name : str = None):
        return VENDOR_GROUPS.get(group_name, VENDORS.keys()) if group_name else VENDORS.keys()
    
    def _sanitize_vendor_name_for_credentials(self, vendor_name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]+', '_', vendor_name).upper()

    def _get_vendor_credentials(self, vendor_name: str):
        '''Returns a dictionary containing the username and password for a given vendor.'''
        sanitized_vendor_name = self._sanitize_vendor_name_for_credentials(vendor_name)

        username = get_env_variable(f'{sanitized_vendor_name}_USERNAME')
        password = get_env_variable(f'{sanitized_vendor_name}_PASSWORD')

        if not username or not password:
            raise ValueError(f"Missing credentials for {vendor_name}. Check your .env file.")

        return {"username": username, "password": password}


    def add_ordering_template_to_all(self, vendors_data: dict) -> dict:
        """
        Adds a default 'ordering' block to each vendor with fields to support
        email, portal, or phone ordering methods.
        """
        for vendor_name, vendor_info in vendors_data.get("vendors", {}).items():
            if "ordering" not in vendor_info:
                vendor_info["ordering"] = {
                    "method": [],           # ["email"], ["portal"], ["phone"], etc.
                    "email": "",
                    "portal_url": "",
                    "phone_number": "",
                    "schedule": [
                        {
                            "order_day": "",
                            "delivery_days": [],
                            "cutoff_time": ""
                        }
                    ]
                }
        return vendors_data


    
    
