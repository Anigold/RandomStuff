class ExportAdapter:

    _ADAPTER_REGISTRY = {}

    preferred_format: str = 'excel' # Default file format

    @classmethod
    def register(cls, vendor: str):
        def decorator(adapter_cls):
            cls._ADAPTER_REGISTRY[vendor.lower()] = adapter_cls()
            return adapter_cls
        return decorator

    @classmethod
    def get_adapter(cls, vendor: str):
        return cls._ADAPTER_REGISTRY.get(vendor.lower(), None)

    def modify_headers(self, headers: list[str]) -> list[str]:
        return headers

    def modify_row(self, row: list, item: object = None) -> list:
        return row

    def modify_workbook(self, workbook: object) -> None:
        pass

    @classmethod
    def get_preferred_format(cls, vendor: str) -> str:
        adapter = cls.get_adapter(vendor)
        return getattr(adapter, 'preferred_format', 'excel')