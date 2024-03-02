from win32 import win32print, win32api, win32console

class Printer:

    def print_file(self, path_to_file: str, printer_name=win32print.GetDefaultPrinter()) -> None:
        printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS} # Doesn't work with PRINTER_ACCESS_USE
        handle = win32print.OpenPrinter(printer_name, printdefaults)
        level = 2
        attributes = win32print.GetPrinter(handle, level)
        
        attributes['pDevMode'].Duplex = 0   #flip over
        win32print.SetPrinter(handle, level, attributes, 0)
        win32print.GetPrinter(handle, level)['pDevMode'].Duplex
        
        win32api.ShellExecute(0, 'print', path_to_file, '.', '.', 0)

        return