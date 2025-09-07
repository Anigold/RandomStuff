from .csv_format import CSVFormat
from .excel_format import ExcelFormat

FORMATS = {
    'csv': CSVFormat(),
    'excel': ExcelFormat(),
    'xlsx': ExcelFormat(),
}

def get_format(name: str):
    fmt = FORMATS.get(name.lower())
    if not fmt:
        raise ValueError(f'Unsupported format: {name}')
    return fmt
