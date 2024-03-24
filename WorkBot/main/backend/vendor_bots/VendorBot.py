from abc import ABC, abstractmethod

class VendorBot(ABC):

    def __init__(self) -> None:
        
        # self.is_logged_in           = False
        # self.driver                 = driver
        # self.username               = username
        # self.password               = password
        self.minimum_order_amount   = 0 # By cents
        self.minimum_order_case     = 0 # By each

    @abstractmethod
    def format_for_file_upload(self, item_data: dict, path_to_save: str):
        pass


class SeleniumBotMixin:

    def __init__(self, driver, username, password) -> None:
        self.is_logged_in = False
        self.driver       = driver
        self.username     = username
        self.password     = password

    def login(self) -> None:
        pass

    def logout(self) -> None:
        pass

    def end_session(self) -> None:
        return self.driver.close()
    

class PricingBotMixin:

    def __init__(self) -> None:
        self.special_cases = {}
    
    def get_pricing_info(self, path_to_pricing_sheet: str) -> dict:
        pass
    
    def get_skus_from_file(self, path_to_skus: str) -> dict:
        pass

    def normalize_units(unit: str) -> str:
        unit = unit.upper()
        units = {
			'#': 'LB',
			'LB': 'LB',
			'CNT': 'EA',
			'EA': 'EA',
			'CT': 'EA',
			'DOZ': 'DZ',
			'PINT': 'PT'
		}

        return units[unit] if unit in units else unit
    
    def helper_iter_rows(sheet):
        for row in sheet.iter_rows():
            yield [cell.value for cell in row]

    def helper_format_size_units(pack: str, size: str) -> list:
		# Check that pack size is float compatible
		
		# if not isinstance(pack, float):
		# 	try:
		# 		pack = float(pack)
		# 	except:
		# 		raise Exception("Pack size is unable to be coerced to float.")

		# Split value and units from size
        unit_string = ''
        size_string = ''
		
        on_number = False
        numeric_non_numerics = ['-', '.']
        for pos, char in enumerate(size):
			
            if char == ' ':
                continue

            if not on_number and char.isnumeric():
                on_number = True
                size_string += char
                continue

            if not on_number and not char.isnumeric():
                if size_string == '': size_string = '1'
                unit_string += char
                continue

            if on_number and char.isnumeric():
                size_string += char
                continue

            if on_number and not char.isnumeric():
                
				
                if char in numeric_non_numerics:
                    size_string += char
                    continue

                if char == '#':
                    unit_string = char
                    break

                on_number = False
                unit_string += char
                continue

        if '-' in size_string:
            lower, upper = size_string.split('-')
            size_string  = (float(lower) + float(upper))/2
        else:
            size_string = float(size_string)

        return [size_string * float(pack), unit_string]
