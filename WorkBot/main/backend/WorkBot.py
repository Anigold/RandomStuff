from backend.logger.Logger import Logger
from backend.vendors.VendorManager import VendorManager
from backend.stores.StoreManager import StoreManager
from backend.orders.OrderManager import OrderManager

from backend.craftable_bot.CraftableBot import CraftableBot
from backend.craftable_bot.helpers import generate_craftablebot_args

import backend.config as config


class WorkBot:

    logger = Logger.get_logger('WorkBot', log_file='logs/work_bot.log')

    def __init__(self):

        self.logger.info('Initializing WorkBot...')

        self.vendor_manager = VendorManager()
        self.order_manager  = OrderManager()
        self.store_manager  = StoreManager()

        driver, username, password = generate_craftablebot_args(config.get_full_path('downloads'))
        self.craft_bot = CraftableBot(driver, username, password, order_manager=self.order_manager)
        
        self.logger.info('WorkBot initialized successfully.')

    
    def download_orders(self, stores, vendors=[], download_pdf=True, update=True):
        self.craft_bot.download_orders(stores, vendors, download_pdf, update)