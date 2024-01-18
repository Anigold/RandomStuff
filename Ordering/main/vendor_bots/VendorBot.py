from abc import ABC, abstractmethod

class VendorBot(ABC):

    @abstractmethod
    def login(self):
        pass
    
    @abstractmethod
    def format_for_file_upload(self, item_data: dict, path_to_save: str):
        pass

    @abstractmethod
    def end_session(self) -> None:
        pass