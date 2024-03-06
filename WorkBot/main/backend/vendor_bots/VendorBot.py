from abc import ABC, abstractmethod

class VendorBot(ABC):

        
    @abstractmethod
    def format_for_file_upload(self, item_data: dict, path_to_save: str):
        pass
