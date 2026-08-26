from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class ScopesCommand(Command):
    """
    List store scopes available to the current user.
    """

    name = "scopes"
    description = "List available store scopes."

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
                "scopes does not accept arguments."
            )

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
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

        if not scopes:
            return CommandResult.text(
                "No store scopes are available for this user."
            )

        return CommandResult.table(
            columns=[
                "ID",
                "Name",
                "Type",
            ],
            rows=[
                [
                    scope.id,
                    scope.name,
                    scope.type,
                ]
                for scope in scopes
            ],
            title="Available Store Scopes",
            summary=f"Found {len(scopes)} available scope(s).",
        )