from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)
from .store_scope_cache import get_cached_store_scopes

class UseScopeCommand(Command):
    """
    Select the active store scope for the CLI session.
    """

    name = "use-scope"
    description = "Select the active store scope."

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

        parser.add_argument(
            "--scope",
            "-s",
            required=True,
            help="Store scope name to activate.",
        )

        return parser

    def autocomplete(self, flag: str, text: str):
        if flag not in ("--scope", "-s"):
            return []

        if not self.context.session.is_authenticated:
            return []

        try:
            scopes = get_cached_store_scopes(self.context)

        except (
            WorkBotUnauthorizedError,
            WorkBotConnectionError,
            WorkBotApiError,
        ):
            return []

        return [
            (
                scope.name,
                f"{scope.type} | {scope.id}",
            )
            for scope in scopes
        ]

    def command(self, args):
        parsed = self.arguments().parse_args(args)

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
            )

        requested_scope_name = parsed.scope.strip()

        if not requested_scope_name:
            return CommandResult.error(
                "Scope name cannot be empty."
            )

        try:
            scopes = self.context.api.list_store_scopes()

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

        matching_scopes = [
            scope
            for scope in scopes
            if scope.name.casefold() == requested_scope_name.casefold()
        ]

        if not matching_scopes:
            return CommandResult.error(
                f'Scope "{requested_scope_name}" is not available '
                "to the current user."
            )

        if len(matching_scopes) > 1:
            return CommandResult.error(
                f'Multiple scopes are named "{requested_scope_name}". '
                "Scope names must be unique for CLI selection."
            )

        selected_scope = matching_scopes[0]

        self.context.session.set_active_scope(
            selected_scope.id
        )

        return CommandResult.object(
            {
                "id": selected_scope.id,
                "name": selected_scope.name,
                "type": selected_scope.type,
            },
            title="Active Store Scope",
            summary=(
                f'Active scope set to "{selected_scope.name}".'
            ),
        )