class Vendor:
    def __init__(self, name, address, contact_info):
        self.name = name
        self.address = address
        self.contact_info = contact_info

    def __str__(self):
        return f"Vendor(name={self.name}, address={self.address}, contact_info={self.contact_info})"

    def __repr__(self):
        return self.__str__()