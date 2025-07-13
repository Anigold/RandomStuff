
class Vendor(ABC):
    
    def __init__(self, name, mininmum_amount, minimum_case) -> None:
        self.name = name
        self.minimum_amount = mininmum_amount
        self.minimum_case = minimum_case

    pass
    # name
    # minimum_amount
    # minimum_case

class SeleniumMixin:

    def __init__(self, driver, username, password) -> None:
        self.driver = driver
        self.username = username
        self.password = password


class Renzi(Vendor, SeleniumMixin):

    def __init__(self, name, minimum_amount, minimum_case, driver, username, password) -> None:
        pass
class VendorFactory:
    pass