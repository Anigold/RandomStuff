from __future__ import annotations

import importlib
import pkgutil
import shlex
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Any

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

    def get_completions(
        self,
        document: Document,
        complete_event,
    ) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        items = self.cli.get_completion_items(
            buffer_text=text_before_cursor,
            word_before_cursor=word_before_cursor,
        )

        for item in items:
            text = self.cli._quote_if_needed(item.value)
            yield Completion(
                text=text,
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
                user_input = self.prompt().strip()
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
            except Exception as e:
                self.logger.exception("Unhandled CLI error.")
                print(f"Error: {e}")

        self._exit()

    def _persist_history(self) -> None:
        # FileHistory persists automatically.
        pass

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

        if not stripped:
            return self._complete_commands_with_metadata(word_before_cursor)

        try:
            tokens = shlex.split(buffer_text)
        except ValueError:
            tokens = buffer_text.split()

        if not tokens:
            return self._complete_commands_with_metadata(word_before_cursor)

        if len(tokens) == 1 and not buffer_text.endswith(" "):
            return self._complete_commands_with_metadata(word_before_cursor)

        return self._complete_arguments_with_metadata(
            buffer=buffer_text,
            text=word_before_cursor,
        )

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

        parser = self._get_command_parser(command_name)
        if not parser:
            return []

        possible_flags = list(parser._option_string_actions.keys())
        trailing_space = buffer.endswith(" ")

        current_token = "" if trailing_space else (tokens[-1] if tokens else "")

        # Case 1: currently typing a flag
        if current_token.startswith("--"):
            return self._complete_flags_with_metadata(command_name, text, tokens)

        # Case 2: just typed command + space
        if len(tokens) == 1 and trailing_space:
            return self._complete_flags_with_metadata(command_name, text, tokens)

        active_flag = self._get_active_flag(tokens[1:], possible_flags)
        if not active_flag:
            return self._complete_flags_with_metadata(command_name, text, tokens)

        action = parser._option_string_actions.get(active_flag)
        if not action:
            return []

        if not self._flag_takes_value(action):
            return self._complete_flags_with_metadata(command_name, text, tokens)

        # If current token is a value for the active flag, complete values.
        values_for_active_flag = self._get_flag_values(tokens[1:], active_flag, possible_flags)

        # If the user just ended a value with a space, keep completing values for multi flags.
        if trailing_space:
            if self._flag_accepts_multiple(action):
                return self._complete_flag_values_with_metadata(
                    command_name=command_name,
                    flag=active_flag,
                    text=text,
                    existing_values=values_for_active_flag,
                )
            return self._complete_flags_with_metadata(command_name, text, tokens)

        # Non-trailing-space case:
        # if the current token is not a flag, it's probably a value in progress.
        if current_token and not current_token.startswith("--"):
            return self._complete_flag_values_with_metadata(
                command_name=command_name,
                flag=active_flag,
                text=text,
                existing_values=values_for_active_flag,
            )

        return []

    def _complete_flags_with_metadata(
        self,
        command_name: str,
        text: str,
        tokens: list[str],
    ) -> list[CompletionItem]:
        parser = self._get_command_parser(command_name)
        if not parser:
            return []

        used_flags = {token for token in tokens if token.startswith("--")}
        items: list[CompletionItem] = []

        for flag, action in parser._option_string_actions.items():
            if not flag.startswith(text):
                continue

            # For now, don't suggest the same flag twice.
            # You can relax this later for append-style arguments if desired.
            if flag in used_flags:
                continue

            help_text = getattr(action, "help", "") or ""
            items.append(CompletionItem(value=flag, description=help_text))

        return sorted(items, key=lambda item: item.value)

    def _complete_flag_values_with_metadata(
        self,
        command_name: str,
        flag: str,
        text: str,
        existing_values: list[str] | None = None,
    ) -> list[CompletionItem]:
        existing_values = existing_values or []

        cmd_obj = self.commands.get(command_name)
        handler = self.autocomplete_registry.get(command_name)

        completions = []
        if callable(handler):
            completions = handler(flag, text) or []
        elif hasattr(cmd_obj, "autocomplete") and callable(cmd_obj.autocomplete):
            completions = cmd_obj.autocomplete(flag, text) or []

        items: list[CompletionItem] = []

        for entry in completions:
            item = self._normalize_completion_entry(entry)
            if not item:
                continue

            if not item.value.startswith(text):
                continue

            if item.value in existing_values:
                continue

            items.append(item)

        return sorted(items, key=lambda item: item.value)

    # ==========================================================
    # Completion helpers
    # ==========================================================

    def _normalize_completion_entry(self, entry: Any) -> CompletionItem | None:
        if isinstance(entry, CompletionItem):
            return entry

        if isinstance(entry, tuple) and len(entry) == 2:
            value, description = entry
            return CompletionItem(value=str(value), description=str(description))

        if isinstance(entry, str):
            return CompletionItem(value=entry, description="")

        return None

    def _get_command_parser(self, command_name: str):
        cmd_obj = self.commands.get(command_name)
        if not cmd_obj or not hasattr(cmd_obj, "arguments"):
            return None

        parser = cmd_obj.arguments()
        return parser

    def _get_active_flag(
        self,
        tokens: list[str],
        possible_flags: list[str],
    ) -> str | None:
        active_flag = None

        for token in tokens:
            if token in possible_flags:
                active_flag = token
            elif token.startswith("--"):
                active_flag = None

        return active_flag

    def _get_flag_values(
        self,
        tokens: list[str],
        target_flag: str,
        possible_flags: list[str],
    ) -> list[str]:
        values: list[str] = []
        collecting = False

        for token in tokens:
            if token == target_flag:
                collecting = True
                values = []
                continue

            if token in possible_flags:
                if collecting:
                    break
                continue

            if token.startswith("--"):
                if collecting:
                    break
                continue

            if collecting:
                values.append(token)

        return values

    def _flag_takes_value(self, action: Any) -> bool:
        # Boolean flags like store_true / store_false do not take a value.
        if getattr(action, "nargs", None) == 0:
            return False

        # argparse store_true/store_false typically use const and nargs=0
        # but nargs=0 check is the main one we need.
        return True

    def _flag_accepts_multiple(self, action: Any) -> bool:
        return getattr(action, "nargs", None) in ("+", "*")

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
        parser = self._get_command_parser(command_name)
        if parser:
            return list(parser._option_string_actions.keys())
        return []

    def register_autocomplete(self, command: str, handler: Callable) -> None:
        self.autocomplete_registry[command] = handler

    def _quote_if_needed(self, value: str) -> str:
        """
        Quote completion values that contain whitespace.
        """
        if " " in value or "&" in value:
            return shlex.quote(value)
        return value
    # ==========================================================
    # Input parsing and dispatch
    # ==========================================================

    def handle_command(self, raw: str) -> None:
        command, args = self._parse_input(raw)
        if not command:
            return
        self._dispatch_command(command, args)

    def _parse_input(self, user_input: str) -> tuple[Optional[str], list[str]]:
        try:
            args = shlex.split(user_input)
            command, params = args[0], args[1:]
            self.logger.debug(f"Parsed command='{command}', args={params}")
            return command, params
        except ValueError as ve:
            self.logger.error(f"Failed to parse input '{user_input}': {ve}")
            print(f"Error parsing input: {ve}")
            return None, []

    def _dispatch_command(self, command: str, args: list[str]) -> None:
        if command not in self.commands:
            self.logger.warning(f"Unknown command entered: '{command}'")
            print(f'Unknown command: "{command}". Type "help" for available commands.')
            return

        try:
            self.logger.info(f"Dispatching command: {command} (args={args})")
            self.commands[command].command(args)
            self.logger.info(f"Command '{command}' executed successfully.")
        except Exception as e:
            self._handle_error(command, e)

    def _handle_error(self, context: str, exception: Exception) -> None:
        self.logger.error(f"[Error] {context} failed: {exception}", exc_info=True)
        print(f"[Error] {context}: {exception}")

    def _exit(self) -> None:
        self.logger.info("Exiting CLI.")
        self._cleanup()
        sys.exit(0)