from apps.cli.cli import CLI
from apps.cli.commands.workbot.registry import register_workbot_commands


def create_workbot_cli() -> CLI:
    cli = CLI()
    register_workbot_commands(cli)
    return cli