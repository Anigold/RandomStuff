from __future__ import annotations

import argparse

from apps.cli.commands.command import Command
from apps.cli.commands.command_result import CommandResult
from apps.cli.commands.confirmation_prompt import ConfirmationPromptRequest
from apps.cli.api.client import (
    WorkBotApiError, 
    WorkBotConnectionError, 
    WorkBotUnauthorizedError
)
from .item_cache import get_cached_items

class DeactivateItemCommand(Command):
    """
    Deactivate an existing WorkBot item.
    """

    name = "deactivate-item"
    description = "Deactivate an existing item."

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

        return parser

    def autocomplete(self, flag: str, text: str):

        if flag not in ("--item", "-i"):
            return []

        if not self.context.session.is_authenticated:
            return []

        if self.context.session.active_scope_id is None:
            return []

        try:

            items = get_cached_items(self.context)

            items = [
                item
                for item in items
                if item.is_active
            ]

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

        try:
            scopes = self.context.api.list_store_scopes()

            active_scope = next(
                (
                    scope
                    for scope in scopes
                    if scope.id
                    == self.context.session.active_scope_id
                ),
                None,
            )

            if active_scope is None:
                self.context.session.set_active_scope(None)

                return CommandResult.error(
                    "The selected scope is no longer available."
                )

            if not active_scope.is_supervisor:
                return CommandResult.error(
                    "Item deactivation requires Supervisor scope."
                )

            item_name = parsed.item.strip()

            selected_item = self.context.api.find_item_by_name(
                item_name,
                include_inactive=True,
            )

            if selected_item is None:
                return CommandResult.error(
                    f'Item "{item_name}" was not found.'
                )

            if not selected_item.is_active:
                return CommandResult.text(
                    f'Item "{selected_item.name}" is already inactive.'
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

        return ConfirmationPromptRequest(
            prompt=(
                f'Deactivate item "{selected_item.name}"?'
            ),
            default=False,
            cancel_message="Item deactivation cancelled.",
            handler=lambda confirmed: self._deactivate_item(
                item_id=selected_item.id,
                item_name=selected_item.name,
            ),
        )

    def _deactivate_item(
        self,
        *,
        item_id: str,
        item_name: str,
    ) -> CommandResult:
        try:
            item = self.context.api.deactivate_item(
                item_id
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
            item,
            title="Deactivated Item",
            summary=(
                f'Deactivated item "{item_name}" successfully.'
            ),
        )