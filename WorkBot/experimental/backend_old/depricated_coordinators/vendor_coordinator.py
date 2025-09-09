# import importlib
# import re
# from config.secrets import get_env_variable
# from backend.helpers.selenium_helpers import create_driver, create_options
# from config.paths import DOWNLOADS_DIR
# from data.VendorRegistry import VENDOR_REGISTRY, VENDOR_GROUPS

# class VendorCoordinator:
#     def __init__(self):
#         self.active_vendors = {}

#     def _sanitize(self, name):
#         return re.sub(r'[^a-zA-Z0-9]+', '_', name).upper()

#     def _get_credentials(self, name):
#         name = self._sanitize(name)
#         return {
#             'username': get_env_variable(f'{name}_USERNAME'),
#             'password': get_env_variable(f'{name}_PASSWORD')
#         }

#     def get_bot_instance(self, vendor_name, driver=None):
#         if vendor_name in self.active_vendors:
#             return self.active_vendors[vendor_name]

#         config = VENDOR_REGISTRY[vendor_name]
#         module = importlib.import_module(config['module_path'])
#         bot_class = getattr(module, config['bot_class'])

#         if config.get('uses_selenium', False):
#             driver = driver or create_driver(create_options(DOWNLOADS_DIR))

#         kwargs = {}
#         if config.get('requires_credentials', False):
#             kwargs.update(self._get_credentials(vendor_name))

#         self.active_vendors[vendor_name] = bot_class(driver, **kwargs)
#         return self.active_vendors[vendor_name]

from backend.storage.file.vendor_file_handler import VendorFileHandler
from pathlib import Path
from config.paths import VENDOR_FILES_DIR
from backend.utils.logger import Logger

@Logger.attach_logger
class VendorCoordinator:

    def __init__(self,):
        self.file_handler = VendorFileHandler()
        self.catalog = self.file_handler.load_all()  # defaults to vendors.yaml

    def get_vendor_information(self, vendor_name: str):
        return self.catalog[vendor_name]
    
    def list_vendors(self) -> list:
        return [vendor for vendor in self.catalog]

    # def get_bot(self, name: str):
    #     return create_vendor_bot(name, self.driver, self.username, self.password)


    # def retrieve_pricing_info(self, vendor: str, path_to_sheet: str):
    #     bot = self.get_bot(vendor)
    #     if isinstance(bot, PricingBotMixin):
    #         return bot.get_pricing_info_from_sheet(path_to_sheet)
    #     raise ValueError(f'{vendor} does not support pricing extraction.')
