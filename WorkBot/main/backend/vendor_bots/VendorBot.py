from abc import ABC, abstractmethod

class VendorBot(ABC):

    def __init__(self, driver, username, password) -> None:
        
        self.is_logged_in           = False
        self.driver                 = driver
        self.username               = username
        self.password               = password
        self.minimum_order_amount   = 0 # In cents
        self.minimum_order_case     = 0 # In cents

    @abstractmethod
    def format_for_file_upload(self, item_data: dict, path_to_save: str):
        pass
