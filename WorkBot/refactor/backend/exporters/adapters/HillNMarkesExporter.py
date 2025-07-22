# backend/exporters/adapters/hillnmarkes.py

from backend.exporters.adapters.Adapter import ExportAdapter

@ExportAdapter.register("Hill & Markes")
class HillNMarkesAdapter(ExportAdapter):
    def modify_headers(self, headers: list[str]) -> list[str]:
        return ["Key Word", "Quantity"]

    def modify_row(self, row: list, item: object = None) -> list:
        return [item.sku, item.quantity]
