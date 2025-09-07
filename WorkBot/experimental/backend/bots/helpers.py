import undetected_chromedriver as uc

def create_options(downloads_path) -> uc.ChromeOptions:

    options = uc.ChromeOptions()
    preferences = {
        'plugins.plugins_list':               [{'enabled': False, 'name': 'Chrome PDF Viewer'}],
        'download.default_directory':         str(downloads_path), # Needs to be casted to a string for proper Chrome Driver handling.
        'download.prompt_for_download':       False,
        'safebrowsing.enabled':               True,
        'plugins.always_open_pdf_externally': True,
        'download.directory_upgrade':         True,
    }
    options.add_experimental_option('prefs', preferences)
    
    return options

def create_driver(options):
    return uc.Chrome(options=options, use_subprocess=True)

