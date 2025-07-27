from backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("UNFI")
class UNFIAdapter(ExportAdapter):

    preferred_format = "csv"
    preferred_delimiter = ","  # Ensure file is saved as .csv

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return ["Item Code", "Quantity"]

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return [item.sku, float(item.quantity)]
