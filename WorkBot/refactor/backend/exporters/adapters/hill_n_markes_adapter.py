from WorkBot.refactor.backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("Hill & Markes")
class HillNMarkesAdapter(ExportAdapter):
    def modify_headers(self, headers: list[str]) -> list[str]:
        return ["Key Word", "Quantity"]

    def modify_row(self, row: list, item: object = None) -> list:
        return [item.sku, item.quantity]
