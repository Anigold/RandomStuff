from typing import Dict

from .base_format import BaseFormatter
from .excel_format import ExcelFormatter
from .csv_format import CsvFormatter
from .json_format import JSONFormatter

from .vendor_formats import * 

_FORMATTERS: Dict[str, BaseFormatter] = {

    'xlsx':               ExcelFormatter,
    'csv':                CsvFormatter,
    'json':               JSONFormatter,
    'sysco':              SyscoFormatter,
    'hill & markes':      HillNMarkesFormatter,
    'unfi':               UNFIFormatter, 
    'performance food':   PerformanceFoodFormatter,
    'us foods':           USFoodsFormatter,

}

def get_formatter(fmt: str) -> BaseFormatter:
    '''Retrieve a formatter by name, raises KeyError if not found.'''
    fmt = fmt.strip().lower()
    return _FORMATTERS[fmt]()
