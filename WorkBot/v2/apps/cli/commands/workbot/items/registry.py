from apps.cli.cli import CLI

from .create_item import CreateItemCommand
from .deactivate_item import DeactivateItemCommand
from .item import ItemCommand
from .items import ItemsCommand
from .reactivate_item import ReactivateItemCommand
from .update_item import UpdateItemCommand
from .add_item_store_info import AddItemStoreInfoCommand
from .update_item_store_info import UpdateItemStoreInfoCommand

def register_item_commands(cli: CLI) -> None:
    cli.load_commands_from_package("apps.cli.commands.workbot.items", cli.command_context)
