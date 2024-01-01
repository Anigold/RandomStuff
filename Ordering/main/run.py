from main.craftable_bot.CraftableBot import CraftableBot
import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
from os import getenv

driver = uc.Chrome(use_subprocess=True)

dotenv = load_dotenv()

username = getenv('CRAFTABLE_USERNAME')
password = getenv('CRAFTABLE_PASSWORD')

stores = [
#     'DOWNTOWN',
#     'EASTHILL',
#     'TRIPHAMMER',
#     'BAKERY'
     'COLLEGETOWN'
]

if __name__ == '__main__':
    craft_bot = CraftableBot(driver, username, password)

    craft_bot.login()

    for store in stores:
        craft_bot.get_orders(store, '12/31/2023')

    time.sleep(20)
    craft_bot.close_session()