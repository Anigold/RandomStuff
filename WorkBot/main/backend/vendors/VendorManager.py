import logging
import importlib
from backend.vendors.vendor_config import get_vendor_information, get_vendor_credentials
from backend.helpers.selenium_helpers import create_driver, create_options
from pathlib import Path

SOURCE_PATH         = Path(__file__).parent.parent
ORDERS_DIRECTORY    = SOURCE_PATH / 'orders' / 'OrderFiles'
DOWNLOADS_DIRECTORY = SOURCE_PATH / 'downloads'

class VendorManager:
    """Manages vendor bot instances dynamically."""
    
    def __init__(self):
        self.active_vendors = {} 

    def initialize_vendor(self, vendor_name, driver=None):
        """Creates and stores a vendor bot instance."""
        if vendor_name in self.active_vendors:
            logging.info(f"{vendor_name} bot is already initialized.")
            return self.active_vendors[vendor_name]

        vendor_info = get_vendor_information(vendor_name)
        if not vendor_info:
            raise ValueError(f"No vendor configuration found for {vendor_name}")

        try:
            module = importlib.import_module(vendor_info['module_path'])
            bot_class = getattr(module, vendor_info['bot_class'])
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not load {vendor_info['bot_class']} for {vendor_name}: {e}")

        init_args = []
        init_kwargs = {}

        if vendor_info.get('uses_selenium', False):
            if not driver: 
                driver = create_driver(create_options(DOWNLOADS_DIRECTORY))
                
            init_args.append(driver)

        if vendor_info.get('requires_credentials', False):
            credentials = get_vendor_credentials(vendor_name)
            init_kwargs.update({
                'username': credentials['username'],
                'password': credentials['password']
            })
            
        bot_instance = bot_class(*init_args, **init_kwargs)
        self.active_vendors[vendor_name] = bot_instance
        logging.info(f"Initialized {vendor_name} bot.")
        return bot_instance

    def get_active_vendor(self, vendor_name):
        """Retrieves an already initialized vendor instance."""
        return self.active_vendors.get(vendor_name)

    def close_all_vendors(self):
        """Logs out and closes all active vendor sessions."""
        for vendor, bot in self.active_vendors.items():
            if hasattr(bot, "logout"):
                bot.logout()
            logging.info(f"Closed session for {vendor}.")
        self.active_vendors.clear()

    def close_vendor(self, vendor_name):
        """Logs out and removes a specific vendor instance."""
        bot = self.active_vendors.get(vendor_name)
        if bot and hasattr(bot, "logout"):
            bot.logout()
        self.active_vendors.pop(vendor_name, None)
        logging.info(f"Closed session for {vendor_name}.")

    def get_vendor_information(self, vendor_name: str) -> dict:
        return get_vendor_information(vendor_name)
    
    # def get_order_format(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get("order_format", "CSV")

    # def vendor_requires_credentials(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get("requires_credentials", False)

    # def vendor_uses_selenium(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get("uses_selenium", False)

    # def get_min_order_value(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get("min_order_value", 0)

    # def get_vendor_notes(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get("special_notes", "")

    # def get_vendor_contacts(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get('inside_contacts', '')

    # def get_special_notes(vendor_name):
    #     return VENDORS.get(vendor_name, {}).get('special_notes', '')

    # def get_vendor_information(vendor_name: str, requested_info: str):

    #     information = {
    #         "uses_selenium": vendor_uses_selenium,
    #         "requires_credentials": vendor_requires_credentials,
    #         "order_format": get_order_format,
    #         "min_order_value": get_min_order_value,
    #         "special_notes": get_special_notes,
    #         "internal_contacts": get_vendor_contacts
    #     }

    #     information_request_callback = information.get(requested_info)
    #     if not information_request_callback:
    #         raise ValueError(f"{requested_info} not valid request.")
        
    #     return information_request_callback(vendor_name)
