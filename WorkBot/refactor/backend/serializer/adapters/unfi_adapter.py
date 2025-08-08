from backend.serializer.adapters.base_adapter import BaseAdapter

@BaseAdapter.register("UNFI")
class UNFIAdapter(BaseAdapter):

    preferred_format = "csv"
    preferred_delimiter = ","  # Ensure file is saved as .csv

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return ["Item Code", "Quantity"]

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return [item.sku, float(item.quantity)]
