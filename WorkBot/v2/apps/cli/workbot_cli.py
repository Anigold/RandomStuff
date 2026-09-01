from apps.cli.cli import CLI
from apps.cli.commands.workbot.registry import register_workbot_commands
from apps.cli.cache import ITEM_CACHE

def register_workbot_caches(cli: CLI) -> None:
    cli.session.cache.register(ITEM_CACHE, scope_sensitive=True)

def create_workbot_cli() -> CLI:
    cli = CLI()
    register_workbot_caches(cli)
    register_workbot_commands(cli)
    return cli