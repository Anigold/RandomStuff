

class Store:
    def __init__(self, store_id: str, name: str, address: str = None):
        self.store_id = store_id
        self.name     = name
        self.address  = address

    def to_dict(self):
        return {
            "store_id": self.store_id,
            "name":     self.name,
            "address":  self.address
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["store_id"], data["name"], data.get("address"))

    def __repr__(self):
        return f"Store({self.store_id}, {self.name}, {self.address})"

