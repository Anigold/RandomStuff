from win32 import win32print, win32api, win32console

name = win32print.GetDefaultPrinter() # verify that it matches with the name of your printer
schedule = {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }
printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS} # Doesn't work with PRINTER_ACCESS_USE
handle = win32print.OpenPrinter(name, printdefaults)
level = 2
attributes = win32print.GetPrinter(handle, level)
#attributes['pDevMode'].Duplex = 1  #no flip
#attributes['pDevMode'].Duplex = 2  #flip up
attributes['pDevMode'].Duplex = 3   #flip over
win32print.SetPrinter(handle, level, attributes, 0)
win32print.GetPrinter(handle, level)['pDevMode'].Duplex
file_to_print = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main\\Schedules\\Monday.pdf'
win32api.ShellExecute(0, 'print', file_to_print, '.', '.', 0)






    
