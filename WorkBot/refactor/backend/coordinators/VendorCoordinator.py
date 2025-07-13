import importlib
import re
from config.secrets import get_env_variable
from backend.helpers.selenium_helpers import create_driver, create_options
from config.paths import DOWNLOADS_DIR
from data.VendorRegistry import VENDOR_REGISTRY, VENDOR_GROUPS

class VendorCoordinator:
    def __init__(self):
        self.active_vendors = {}

    def _sanitize(self, name):
        return re.sub(r'[^a-zA-Z0-9]+', '_', name).upper()

    def _get_credentials(self, name):
        name = self._sanitize(name)
        return {
            "username": get_env_variable(f"{name}_USERNAME"),
            "password": get_env_variable(f"{name}_PASSWORD")
        }

    def get_bot_instance(self, vendor_name, driver=None):
        if vendor_name in self.active_vendors:
            return self.active_vendors[vendor_name]

        config = VENDOR_REGISTRY[vendor_name]
        module = importlib.import_module(config["module_path"])
        bot_class = getattr(module, config["bot_class"])

        if config.get("uses_selenium", False):
            driver = driver or create_driver(create_options(DOWNLOADS_DIR))

        kwargs = {}
        if config.get("requires_credentials", False):
            kwargs.update(self._get_credentials(vendor_name))

        self.active_vendors[vendor_name] = bot_class(driver, **kwargs)
        return self.active_vendors[vendor_name]
