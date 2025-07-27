from backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("Sysco")
class SyscoAdapter(ExportAdapter):

    preferred_format = "csv"

    def modify_headers(self, headers: list[str], context: dict = None) -> list[str]:
        # Sysco expects no header row
        return []

    def modify_row(self, row: list, item: object = None, context: dict = None) -> list:
        return ["P", item.sku, int(item.quantity), 0]
