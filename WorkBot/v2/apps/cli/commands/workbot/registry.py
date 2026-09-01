from apps.cli.cli import CLI

from .items.registry import register_item_commands
# from .orders.registry import register_order_commands
# from .stores.registry import register_store_commands
# from .vendors.registry import register_vendor_commands


def register_workbot_commands(cli: CLI) -> None:
    register_item_commands(cli)
    # register_order_commands(cli)
    # register_store_commands(cli)
    # register_vendor_commands(cli)