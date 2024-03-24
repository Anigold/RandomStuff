from ..vendor_bots.VendorBot import PricingBotMixin

class PriceComparator:

    def compare_prices(self, pricing_bots: list[PricingBotMixin], output_file_path: str) -> None:
        pass
        '''
        for bot in pricing_bots:
            bot.get_pricing_info_from_sheet(path_to_sheet)

        '''