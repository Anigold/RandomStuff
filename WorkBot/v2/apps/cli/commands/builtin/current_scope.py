from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class CurrentScopeCommand(Command):
    """
    Show the currently active store scope.
    """

    name = "current-scope"
    description = "Show the currently active store scope."

    def arguments(self):
        return argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        return []

    def command(self, args):
        if args:
            return CommandResult.error(
                "current-scope does not accept arguments."
            )

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
            )

        active_scope_id = self.context.session.active_scope_id

        if active_scope_id is None:
            return CommandResult.text(
                "No store scope is currently selected."
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

        active_scope = next(
            (
                scope
                for scope in scopes
                if scope.id == active_scope_id
            ),
            None,
        )

        if active_scope is None:
            self.context.session.set_active_scope(None)

            return CommandResult.error(
                "The currently selected scope is no longer available. "
                "The active scope has been cleared."
            )

        return CommandResult.object(
            {
                "id": active_scope.id,
                "name": active_scope.name,
                "type": active_scope.type,
            },
            title="Current Store Scope",
            summary=(
                f'Current scope: "{active_scope.name}".'
            ),
        )