from __future__ import annotations

import importlib
import pkgutil
import shlex
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import CompleteStyle

from backend.infra.logger import Logger
from backend.infra.paths import CLI_HISTORY_FILE
from .commands.command import Command
from .commands.command_context import CommandContext


@dataclass
class CompletionItem:
    value: str
    description: str = ""


class CLICompleter(Completer):
    def __init__(self, cli: "CLI"):
        self.cli = cli

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        text = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        items = self.cli.get_completion_items(text, word_before_cursor)

        for item in items:
            yield Completion(
                text=item.value,
                start_position=-len(word_before_cursor),
                display=item.value,
                display_meta=item.description,
            )


@Logger.attach_logger
class CLI:
    def __init__(self) -> None:
        self.commands: dict[str, Command] = {}
        self.autocomplete_registry: dict[str, Callable[[str, str], list]] = {}

        self.logger.info("Initializing CLI.")

        self._register_builtin_commands()
        self.session = self._build_prompt_session()

        self.logger.info(
            f"CLI initialized successfully with {len(self.commands)} commands."
        )

    # ==========================================================
    # Prompt toolkit session
    # ==========================================================

    def _build_prompt_session(self) -> PromptSession:
        return PromptSession(
            completer=CLICompleter(self),
            history=FileHistory(str(CLI_HISTORY_FILE)),
            complete_while_typing=True,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )

    def prompt(self) -> str:
        return self.session.prompt("WorkBot> ")

    def cmdloop(self) -> None:
        while True:
            try:
                raw = self.prompt().strip()
                if not raw:
                    continue

                self.handle_command(raw)

            except (EOFError, KeyboardInterrupt):
                print()
                break
            except Exception as e:
                self.logger.exception("Unhandled CLI error.")
                print(f"Error: {e}")

    # ==========================================================
    # Command registration
    # ==========================================================

    def _register_builtin_commands(self, context: CommandContext | None = None) -> None:
        from backend.app.cli.commands.command_context import CommandContext
        context = context or CommandContext(cli=self)
        self.load_commands_from_package("backend.app.cli.commands.builtin", context)

    def load_commands_from_package(self, package_name: str, context: dict | None) -> None:
        package = importlib.import_module(package_name)
        count = 0

        for _, mod_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if is_pkg:
                continue

            module = importlib.import_module(f"{package_name}.{mod_name}")

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Command)
                    and attr is not Command
                ):
                    cmd = attr(context)
                    self.commands[cmd.name] = cmd

                    if callable(getattr(cmd, "autocomplete", None)):
                        self.autocomplete_registry[cmd.name] = cmd.autocomplete

                    count += 1

        self.logger.info(f"Loaded {count} commands from {package_name}")

    # ==========================================================
    # Completion API used by CLICompleter
    # ==========================================================

    def get_completion_items(
        self,
        buffer_text: str,
        word_before_cursor: str,
    ) -> list[CompletionItem]:
        stripped = buffer_text.lstrip()

        if not stripped or " " not in stripped:
            return self._complete_commands_with_metadata(word_before_cursor)

        return self._complete_arguments_with_metadata(buffer_text, word_before_cursor)

    def _complete_commands_with_metadata(self, text: str) -> list[CompletionItem]:
        items: list[CompletionItem] = []

        for name, cmd in self.commands.items():
            if name.startswith(text):
                items.append(
                    CompletionItem(
                        value=name,
                        description=self._get_command_description(cmd),
                    )
                )

        return sorted(items, key=lambda item: item.value)

    def _complete_arguments_with_metadata(
        self,
        buffer: str,
        text: str,
    ) -> list[CompletionItem]:
        try:
            tokens = shlex.split(buffer)
        except ValueError:
            tokens = buffer.split()

        if not tokens:
            return []

        command_name = tokens[0]
        cmd_obj = self.commands.get(command_name)

        if not cmd_obj:
            return []

        possible_flags = self._get_command_flags(command_name)

        trailing_space = buffer.endswith(" ")
        current_token = "" if trailing_space else (tokens[-1] if tokens else "")
        previous_token = tokens[-1] if trailing_space and tokens else (
            tokens[-2] if len(tokens) >= 2 else ""
        )

        # Completing a flag
        if current_token.startswith("--") or (
            trailing_space and (not previous_token or not previous_token.startswith("--"))
        ):
            return self._complete_flags_with_metadata(command_name, text)

        # Completing a value for a flag
        flag_for_values = None
        if trailing_space and tokens and tokens[-1].startswith("--"):
            flag_for_values = tokens[-1]
        elif len(tokens) >= 2 and tokens[-2].startswith("--"):
            flag_for_values = tokens[-2]

        if flag_for_values and flag_for_values in possible_flags:
            return self._complete_flag_values_with_metadata(
                command_name,
                flag_for_values,
                text,
            )

        return []

    def _complete_flags_with_metadata(
        self,
        command_name: str,
        text: str,
    ) -> list[CompletionItem]:
        cmd_obj = self.commands.get(command_name)
        parser = cmd_obj.arguments() if hasattr(cmd_obj, "arguments") else None

        if not parser:
            return []

        items: list[CompletionItem] = []

        for flag, action in parser._option_string_actions.items():
            if flag.startswith(text):
                help_text = getattr(action, "help", "") or ""
                items.append(CompletionItem(value=flag, description=help_text))

        return sorted(items, key=lambda item: item.value)

    def _complete_flag_values_with_metadata(
        self,
        command_name: str,
        flag: str,
        text: str,
    ) -> list[CompletionItem]:
        cmd_obj = self.commands.get(command_name)
        handler = self.autocomplete_registry.get(command_name)

        completions = []
        if callable(handler):
            completions = handler(flag, text) or []
        elif hasattr(cmd_obj, "autocomplete") and callable(cmd_obj.autocomplete):
            completions = cmd_obj.autocomplete(flag, text) or []

        items: list[CompletionItem] = []

        for entry in completions:
            if isinstance(entry, CompletionItem):
                if entry.value.startswith(text):
                    items.append(entry)

            elif isinstance(entry, tuple) and len(entry) == 2:
                value, description = entry
                if value.startswith(text):
                    items.append(CompletionItem(value=value, description=description))

            elif isinstance(entry, str):
                if entry.startswith(text):
                    items.append(CompletionItem(value=entry, description=""))

        return sorted(items, key=lambda item: item.value)

    # ==========================================================
    # Helpers
    # ==========================================================

    def _get_command_description(self, cmd: Command) -> str:
        for attr in ("description", "help", "summary"):
            value = getattr(cmd, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        doc = getattr(cmd, "__doc__", None)
        if isinstance(doc, str) and doc.strip():
            return doc.strip().splitlines()[0]

        return ""

    def _get_command_flags(self, command_name: str) -> list[str]:
        cmd_obj = self.commands.get(command_name)
        if hasattr(cmd_obj, "arguments"):
            parser = cmd_obj.arguments()
            if parser:
                return list(parser._option_string_actions.keys())
        return []

    def register_autocomplete(self, command: str, handler: Callable) -> None:
        self.autocomplete_registry[command] = handler

    # ==========================================================
    # Your existing execution hook
    # ==========================================================

    def handle_command(self, raw: str) -> None:
        """
        Replace this with your existing parse/dispatch logic.
        """
        print(f"Executing: {raw}")



    def start(
            self,
            welcome_screen: str = '\nWelcome to your CLI. Type "help" to see available commands.\n',
        ) -> None:
            self.logger.info("CLI session started.")
            print(welcome_screen)
            self._run()

    def _run(self) -> None:
        while True:
            try:
                user_input = self.session.prompt("WorkBot> ").strip()
                if not user_input:
                    continue

                self.logger.debug(f"User input received: {user_input}")

                command, args = self._parse_input(user_input)
                if not command:
                    continue

                if command in ("exit", "quit"):
                    self.logger.info("User requested CLI shutdown.")
                    break

                self._dispatch_command(command, args)

            except (KeyboardInterrupt, EOFError):
                self.logger.info("CLI interrupted by user.")
                print("\nExiting CLI.")
                break

        self._exit()

    def _persist_history(self) -> None:
        # prompt_toolkit FileHistory persists automatically
        pass

    def _exit(self) -> None:
        self.logger.info("Exiting CLI.")
        self._cleanup()
        sys.exit(0)