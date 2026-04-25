from ..command import Command
import argparse


from backend.app.cli.commands.command_result import CommandResult
from backend.core.utils.datetimes import convert_date_format


class DisplayItemDetails(Command):
    name = "display_item_details"

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description="Display the general information for a single item.",
        )
        parser.add_argument(
            "--item",
            required=True,
            help="The item.",
        )
        
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            "--item": self.context.get_items,
        }

        return [
            option
            for option in flags.get(flag, [])()
            if option.startswith(text)
        ]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)

            item = self.context.workbot.get_item_by_name(parsed_args.item)

            # orders = self.context.workbot.get_orders(
            #     stores=[parsed_args.store],
            #     vendors=[parsed_args.vendor],
            # )

            if not item:
                return CommandResult(
                    kind="error",
                    payload="No item found.",
                    target="console",
                )

            # order = orders[0]

            # if not order.items:
            #     return CommandResult(
            #         kind="text",
            #         payload=self._format_order_summary(order),
            #         target="side",
            #         title="Order Summary",
            #         summary="Order found, but no items were present.",
            #     )

            detail_text = self._format_item_detail(item)

            return CommandResult(
                kind="text",
                payload=detail_text,
                target="side",
                title=f"Order: {item.name}",
                summary=(
                    f"Loaded info for {item.name}"
                ),
            )

        except SystemExit:
            return CommandResult(
                kind="error",
                payload="Invalid arguments provided.",
                target="console",
            )

   
    def _format_item_detail(self, item) -> str:
        return f'''

{item.name}
{item.id}
{item.category}
{item.subcategory}
Is Active: {item.is_active}
Is Inventoried: {item.is_inventoried}
{item.notes}
{item.aliases}

'''