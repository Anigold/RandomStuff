from apps.cli.cli import CLI

def register_item_commands(cli: CLI) -> None:
    cli.load_commands_from_package("apps.cli.commands.workbot.items", cli.command_context)
