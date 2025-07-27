from backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("Hill & Markes")
class HillNMarkesAdapter(ExportAdapter):

    preferred_format = 'excel'

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return ["Key Word", "Quantity"]

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return [item.sku, item.quantity]

