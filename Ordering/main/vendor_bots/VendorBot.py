from abc import ABC, abstractmethod

class VendorBot(ABC):

    @abstractmethod
    def login(self):
        pass
