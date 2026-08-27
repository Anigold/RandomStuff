from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class ItemsCommand(Command):
    """
    List items available in the current store scope.
    """

    name = "items"
    description = "List items in the current store scope."

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

        parser.add_argument(
            "--search",
            "-s",
            help="Filter items by name.",
        )

        parser.add_argument(
            "--include-inactive",
            action="store_true",
            help="Include inactive items.",
        )

        return parser

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        return []

    def command(self, args):
        parsed = self.arguments().parse_args(args)

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
            )

        if self.context.session.active_scope_id is None:
            return CommandResult.error(
                "No store scope is selected. "
                'Use "use-scope" first.'
            )

        try:
            items = self.context.api.list_items(
                search=parsed.search,
                include_inactive=parsed.include_inactive,
            )

        except WorkBotUnauthorizedError:
            self.context.session.logout()

            return CommandResult.error(
                "Your authentication session is no longer valid. "
                "Please log in again."
            )

        except WorkBotConnectionError as exc:
            return CommandResult.error(str(exc))

        except WorkBotApiError as exc:
            return CommandResult.error(str(exc))

        if not items:
            return CommandResult.text(
                "No items found."
            )

        return CommandResult.table(
            columns=[
                "ID",
                "Name",
                "Category",
                "Subcategory",
                "Active",
            ],
            rows=[
                [
                    item.id,
                    item.name,
                    item.category or "",
                    item.subcategory or "",
                    "Yes" if item.is_active else "No",
                ]
                for item in items
            ],
            title="Items",
            summary=f"Found {len(items)} item(s).",
        )