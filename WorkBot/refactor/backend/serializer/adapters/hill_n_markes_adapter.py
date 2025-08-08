from backend.serializer.adapters.base_adapter import BaseAdapter

@BaseAdapter.register("Hill & Markes")
class HillNMarkesAdapter(BaseAdapter):

    preferred_format = 'excel'

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        return ["Key Word", "Quantity"]

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return [item.sku, item.quantity]

