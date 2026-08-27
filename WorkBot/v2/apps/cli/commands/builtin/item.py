from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class ItemCommand(Command):
    """
    Show details for an item in the current store scope.
    """

    name = "item"
    description = "Show item details."

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

        parser.add_argument(
            "--item",
            "-i",
            required=True,
            help="Item name.",
        )

        parser.add_argument(
            "--include-inactive",
            action="store_true",
            help="Allow selection of inactive items.",
        )

        return parser

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        if flag not in ("--item", "-i"):
            return []

        if not self.context.session.is_authenticated:
            return []

        if self.context.session.active_scope_id is None:
            return []

        try:
            items = self.context.api.list_items(
                search=text or None,
                include_inactive=True,
            )

        except (
            WorkBotUnauthorizedError,
            WorkBotConnectionError,
            WorkBotApiError,
        ):
            return []

        return [
            (
                item.name,
                item.category or item.id,
            )
            for item in items
        ]

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

        item_name = parsed.item.strip()

        if not item_name:
            return CommandResult.error(
                "Item name cannot be empty."
            )

        try:
            item = self.context.api.find_item_by_name(
                item_name,
                include_inactive=parsed.include_inactive,
            )

            if item is None:
                return CommandResult.error(
                    f'Item "{item_name}" was not found '
                    "in the current scope."
                )

            detail = self.context.api.get_item(
                item.id
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

        return CommandResult.object(
            detail,
            title="Item Details",
            summary=f'Loaded item "{item.name}".',
        )