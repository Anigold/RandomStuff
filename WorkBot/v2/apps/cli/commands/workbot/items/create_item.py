from __future__ import annotations

import argparse
from typing import Any

from apps.cli.commands.command import Command
from apps.cli.commands.command_result import CommandResult
from apps.cli.api.client import (
    WorkBotApiError, 
    WorkBotConnectionError, 
    WorkBotUnauthorizedError,

)
from apps.cli.commands.form_parsers import (
    parse_bool, 
    parse_decimal,
)
from apps.cli.commands.form_prompt import (
    FormField,
    FormPromptRequest
)

from apps.cli.api.client import (
    ItemWritePayload,
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)

class CreateItemCommand(Command):
    """
    Create a new WorkBot item.
    """

    name = "create-item"
    description = "Create a new item."

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
                "create-item does not accept arguments."
            )

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
                "Item creation requires Supervisor scope."
            )

        return FormPromptRequest(
            title="Create Item",
            cancel_message="Item creation cancelled.",
            fields=self._fields(),
            handler=self._create_item,
        )

    def _fields(self) -> list[FormField]:
        return [
            FormField(
                name="name",
                prompt="Name",
                required=True,
            ),
            FormField(
                name="category",
                prompt="Category",
            ),
            FormField(
                name="subcategory",
                prompt="Subcategory",
            ),
            FormField(
                name="count_unit_quantity",
                prompt="Count unit quantity",
                parser=parse_decimal,
            ),
            FormField(
                name="count_unit_measure",
                prompt="Count unit measure",
            ),
            FormField(
                name="custom_each_name",
                prompt="Custom each name",
            ),
            FormField(
                name="each_quantity",
                prompt="Each quantity",
                parser=parse_decimal,
            ),
            FormField(
                name="each_measure",
                prompt="Each measure",
            ),
            FormField(
                name="weight_quantity",
                prompt="Weight quantity",
                parser=parse_decimal,
            ),
            FormField(
                name="weight_measure",
                prompt="Weight measure",
            ),
            FormField(
                name="volume_quantity",
                prompt="Volume quantity",
                parser=parse_decimal,
            ),
            FormField(
                name="volume_measure",
                prompt="Volume measure",
            ),
            FormField(
                name="is_active",
                prompt="Active",
                default=True,
                parser=parse_bool,
            ),
        ]

    def _create_item(
        self,
        values: dict[str, Any],
    ) -> CommandResult:
        try:
            payload = ItemWritePayload.from_dict(
                values
            )

            item = self.context.api.create_item(
                payload
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

        item_name = item.get(
            "name",
            values["name"],
        )

        return CommandResult.object(
            item,
            title="Created Item",
            summary=(
                f'Created item "{item_name}" successfully.'
            ),
        )