
from openpyxl import load_workbook

SOURCE_PATH = 'C:\\Users\\Will\\Desktop\\Andrew\\Projects\\RandomStuff\\WorkBot\\main'
PRICING_PATH = f'{SOURCE_PATH}\\backend\\pricing'

PRICING_GUIDES_PATH = f'{PRICING_PATH}\\Pricing Guides'

price_guides = ['IBFavorite', 'IBProduce']

def get_data_from_price_guide(guide_path: str) -> dict:
    workbook = load_workbook(guide_path)
    sheet = workbook.active

    