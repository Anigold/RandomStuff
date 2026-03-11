from .csv_format import CsvFormatter

class TxtFormatter(CsvFormatter):

    def format_name(self) -> str:
        return 'txt'