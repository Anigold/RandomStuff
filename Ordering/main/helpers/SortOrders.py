    # Sort and group orders
files = get_files(download_path)
for file in files:
    
    vendor_name = file.split('_')[0].strip()
    print(vendor_name)

    if not isdir(f'{download_path}{vendor_name}'):
        mkdir(f'{download_path}{vendor_name}')
    
    rename(f'{download_path}{file}', f'{download_path}{vendor_name}\\{file}')