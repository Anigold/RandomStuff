import logging
from backend.vendors.vendor_config import get_vendor_bot, get_vendor_credentials

class VendorManager:
    """Manages vendor bot instances dynamically."""
    
    def __init__(self):
        self.active_vendors = {}

    def initialize_vendor(self, vendor_name, driver=None):
        """Creates and stores a vendor bot instance."""
        if vendor_name in self.active_vendors:
            logging.info(f"✅ {vendor_name} bot is already initialized.")
            return self.active_vendors[vendor_name]

        bot_class = get_vendor_bot(vendor_name)
        if not bot_class:
            raise ValueError(f"⚠️ No bot found for {vendor_name}")

        credentials = get_vendor_credentials(vendor_name)
        if credentials:
            bot_instance = bot_class(driver, credentials["username"], credentials["password"])
        else:
            bot_instance = bot_class(driver)

        self.active_vendors[vendor_name] = bot_instance
        logging.info(f"✅ Initialized {vendor_name} bot.")
        return bot_instance

    def get_active_vendor(self, vendor_name):
        """Retrieves an already initialized vendor instance."""
        return self.active_vendors.get(vendor_name)

    def close_all_vendors(self):
        """Logs out and closes all active vendor sessions."""
        for vendor, bot in self.active_vendors.items():
            if hasattr(bot, "logout"):
                bot.logout()
            logging.info(f"🔴 Closed session for {vendor}.")
        self.active_vendors.clear()

    def close_vendor(self, vendor_name):
        """Logs out and removes a specific vendor instance."""
        bot = self.active_vendors.get(vendor_name)
        if bot and hasattr(bot, "logout"):
            bot.logout()
        self.active_vendors.pop(vendor_name, None)
        logging.info(f"🔴 Closed session for {vendor_name}.")
