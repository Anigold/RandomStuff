from __future__ import annotations

import importlib
import io
import pkgutil
import shlex
import sys
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from backend.infra.logger import Logger
from backend.infra.paths import CLI_HISTORY_FILE
from .commands.command import Command
from .commands.command_context import CommandContext

import importlib
import io
import pkgutil
import shlex
import sys
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window, Float, FloatContainer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.menus import MultiColumnCompletionsMenu


from backend.infra.logger import Logger
from backend.infra.paths import CLI_HISTORY_FILE
from .commands.command import Command
from .commands.command_context import CommandContext


from dataclasses import asdict, is_dataclass
from typing import Any

# from backend.app.contracts.command_result import CommandResult
from dataclasses import dataclass, field
from typing import Any, Literal



from backend.app.cli.commands.command_result import CommandResult


@dataclass
class CompletionItem:
    value: str
    description: str = ""





class CLIResultRenderer:
    def render(self, result: CommandResult) -> dict[str, Any]:
        console_text = result.summary or ""
        side_text = ""
        side_title = result.title or "Details"

        if result.kind == "empty":
            pass

        elif result.kind == "text":
            rendered = str(result.payload or "")
            console_text, side_text = self._place_text(
                rendered,
                result.target,
                console_text,
            )

        elif result.kind == "error":
            rendered = f"[Error] {result.payload}"
            console_text = self._join(console_text, rendered)

        elif result.kind == "list":
            rendered = self._render_list(result.payload)
            console_text, side_text = self._place_text(
                rendered,
                result.target,
                console_text,
            )

        elif result.kind == "object":
            rendered = self._render_object(result.payload)
            console_text, side_text = self._place_text(
                rendered,
                result.target,
                console_text,
            )

        elif result.kind == "table":
            rendered = self._render_table(result.payload)
            console_text, side_text = self._place_text(
                rendered,
                result.target,
                console_text,
            )

        else:
            rendered = str(result.payload)
            console_text, side_text = self._place_text(
                rendered,
                result.target,
                console_text,
            )

        return {
            "console_text": console_text,
            "side_text": side_text,
            "side_title": side_title,
            "replace_side_panel": result.replace_side_panel,
        }

    def _place_text(
        self,
        rendered: str,
        target: str,
        console_text: str,
    ) -> tuple[str, str]:
        side_text = ""

        if target == "console":
            console_text = self._join(console_text, rendered)
        elif target == "side":
            side_text = rendered
        elif target == "both":
            console_text = self._join(console_text, rendered)
            side_text = rendered

        return console_text, side_text

    def _join(self, left: str, right: str) -> str:
        if not left:
            return right
        if not right:
            return left
        return f"{left}\n{right}"

    def _render_list(self, payload: Any) -> str:
        if not payload:
            return "(no results)"
        return "\n".join(f"{i}. {self._stringify(item)}" for i, item in enumerate(payload, start=1))

    def _render_object(self, payload: Any) -> str:
        if payload is None:
            return "(none)"

        if is_dataclass(payload):
            return self._render_mapping(asdict(payload))

        if isinstance(payload, dict):
            return self._render_mapping(payload)

        return self._stringify(payload)

    def _render_mapping(self, mapping: dict[str, Any]) -> str:
        if not mapping:
            return "(empty)"

        width = max(len(str(k)) for k in mapping)
        return "\n".join(
            f"{str(k).ljust(width)} : {self._stringify(v)}"
            for k, v in mapping.items()
        )

    def _render_table(self, payload: Any) -> str:
        if not payload:
            return "(no table data)"

        columns = payload.get("columns", [])
        rows = payload.get("rows", [])

        if not columns:
            return "(invalid table)"

        widths = [len(str(col)) for col in columns]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        def fmt_row(row: list[Any]) -> str:
            return " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

        header = fmt_row(columns)
        divider = "-+-".join("-" * width for width in widths)
        body = [fmt_row(row) for row in rows]

        return "\n".join([header, divider, *body])

    def _stringify(self, value: Any) -> str:
        if isinstance(value, (list, tuple, set)):
            return ", ".join(str(v) for v in value)
        if isinstance(value, dict):
            return "{ " + ", ".join(f"{k}: {v}" for k, v in value.items()) + " }"
        return str(value)
    

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
            insertion_text = self.cli._quote_if_needed(item.value)

            yield Completion(
                text=insertion_text,
                start_position=-len(word_before_cursor),
                display=item.value,
                display_meta=item.description,
            )


@Logger.attach_logger
class CLI:
    def __init__(self) -> None:
        self.commands: dict[str, Command] = {}
        self.autocomplete_registry: dict[str, Callable[[str, str], list]] = {}
        self._parser_cache: dict[str, Any] = {}
        self.result_renderer = CLIResultRenderer()

        self.logger.info("Initializing CLI.")

        self._register_builtin_commands()
        self._build_ui()

        self.logger.info(
            f"CLI initialized successfully with {len(self.commands)} commands."
        )

    # ==========================================================
    # UI bootstrap
    # ==========================================================

    def _build_ui(self) -> None:
        # -------------------------
        # Main output panes
        # -------------------------
        self.console_output = TextArea(
            text="",
            read_only=True,
            scrollbar=True,
            wrap_lines=True,      # good for command history / logs
            focusable=True,
        )

        self.side_output = TextArea(
            text="No details loaded.",
            read_only=True,
            scrollbar=True,
            wrap_lines=False,     # keep tables intact
            focusable=True,
        )

        self.input_field = TextArea(
            height=1,
            prompt="WorkBot> ",
            multiline=False,
            wrap_lines=False,
            completer=CLICompleter(self),
            complete_while_typing=True,
            history=FileHistory(str(CLI_HISTORY_FILE)),
        )

        # -------------------------
        # Frames
        # -------------------------
        self.console_frame = Frame(
            self.console_output,
            title="Console (F6)",
        )

        self.side_frame = Frame(
            self.side_output,
            title="Details (F7)",
        )

        self.input_frame = Frame(
            self.input_field,
            title="Command (F8)",
        )

        # Optional footer/help bar
        self.footer_bar = Window(
            content=FormattedTextControl(
                text=(
                    " F6 Console  |  F7 Details  |  F8 Command  |  "
                    "Esc c Clear Console  |  Esc d Clear Details  |  Ctrl-Q Exit "
                )
            ),
            height=1,
            style="class:footer",
        )

        # -------------------------
        # Layout
        # -------------------------
        output_row = VSplit(
            [
                # Console gets less width than details
                self.console_frame,
                self.side_frame,
            ],
            padding=1,
            width=Dimension(weight=1),
        )

        body = HSplit(
            [
                VSplit(
                    [
                        self.console_frame,
                        self.side_frame,
                    ],
                    padding=1,
                ),
                self.input_frame,
                self.footer_bar,
            ]
        )

        root = FloatContainer(
            content=body,
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=MultiColumnCompletionsMenu(),
                )
            ],
        )

        kb = self._build_keybindings()

        self.application = Application(
            layout=Layout(root, focused_element=self.input_field),
            key_bindings=kb,
            full_screen=True,
            mouse_support=True,
            style=Style.from_dict(
                {
                    "frame.label": "bold",
                    "footer": "reverse",
                }
            ),
        )

    def _build_keybindings(self):
        kb = KeyBindings()

        @kb.add("enter")
        def _(event) -> None:
            raw = self.input_field.text.strip()
            if not raw:
                return

            history = self.input_field.buffer.history
            strings = list(history.get_strings())
            if not strings or strings[-1] != raw:
                history.append_string(raw)

            self.input_field.buffer.reset()
            self.append_console(f"> {raw}")
            self.handle_command(raw)

        @kb.add("c-c")
        @kb.add("c-q")
        def _(event) -> None:
            event.app.exit()

        @kb.add("f6")
        def _(event) -> None:
            event.app.layout.focus(self.console_output)

        @kb.add("f7")
        def _(event) -> None:
            event.app.layout.focus(self.side_output)

        @kb.add("f8")
        def _(event) -> None:
            event.app.layout.focus(self.input_field)

        @kb.add("escape", "c")
        def _(event) -> None:
            self.clear_console()

        @kb.add("escape", "d")
        def _(event) -> None:
            self.clear_side_panel()

        return kb

    def start(
        self,
        welcome_screen: str = '\nWelcome to your CLI. Type "help" to see available commands.\n',
    ) -> None:
        self.logger.info("CLI session started.")
        self.append_console(welcome_screen.strip("\n"))
        self.application.run()
        self._exit()

    # ==========================================================
    # Pane helpers
    # ==========================================================

    def append_console(self, text: str) -> None:
        if not text:
            return

        current = self.console_output.text
        if current and not current.endswith("\n"):
            current += "\n"

        self.console_output.text = current + text.rstrip() + "\n"

    def set_console(self, text: str) -> None:
        self.console_output.text = text.rstrip() + ("\n" if text else "")

    def clear_console(self) -> None:
        self.console_output.text = ""

    def set_side_panel(self, text: str, title: str = "Details") -> None:
        self.side_frame.title = title
        self.side_output.text = text if text else ""

    def append_side_panel(self, text: str, title: str | None = None) -> None:
        if title:
            self.side_frame.title = title

        current = self.side_output.text
        if current and not current.endswith("\n"):
            current += "\n"

        self.side_output.text = current + text.rstrip() + "\n"

    def clear_side_panel(self) -> None:
        self.side_frame.title = "Details"
        self.side_output.text = ""

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
    # Completion entrypoint
    # ==========================================================

    def get_completion_items(
        self,
        buffer_text: str,
        word_before_cursor: str,
    ) -> list[CompletionItem]:
        stripped = buffer_text.lstrip()

        if not stripped:
            return self._complete_commands_with_metadata(word_before_cursor)

        tokens = self._safe_split(buffer_text)

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
        tokens = self._safe_split(buffer)
        if not tokens:
            return []

        command_name = tokens[0]
        parser = self._get_command_parser(command_name)
        if not parser:
            return []

        possible_flags = list(parser._option_string_actions.keys())
        trailing_space = buffer.endswith(" ")
        current_token = "" if trailing_space else (tokens[-1] if tokens else "")

        if current_token.startswith("--"):
            return self._complete_flags_with_metadata(command_name, text, tokens)

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

        existing_values = self._get_flag_values(tokens[1:], active_flag, possible_flags)

        if trailing_space:
            if self._flag_accepts_multiple(action):
                return self._complete_flag_values_with_metadata(
                    command_name=command_name,
                    flag=active_flag,
                    text=text,
                    existing_values=existing_values,
                )
            return self._complete_flags_with_metadata(command_name, text, tokens)

        if current_token and not current_token.startswith("--"):
            return self._complete_flag_values_with_metadata(
                command_name=command_name,
                flag=active_flag,
                text=text,
                existing_values=existing_values[:-1] if existing_values else [],
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

    def _safe_split(self, text: str) -> list[str]:
        try:
            return shlex.split(text)
        except ValueError:
            return text.split()

    def _quote_if_needed(self, value: str) -> str:
        if any(ch.isspace() for ch in value):
            return shlex.quote(value)
        return value

    def _get_command_parser(self, command_name: str):
        if command_name in self._parser_cache:
            return self._parser_cache[command_name]

        cmd_obj = self.commands.get(command_name)
        if not cmd_obj or not hasattr(cmd_obj, "arguments"):
            return None

        parser = cmd_obj.arguments()
        self._parser_cache[command_name] = parser
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

            if token in possible_flags or token.startswith("--"):
                if collecting:
                    break
                continue

            if collecting:
                values.append(token)

        return values

    def _flag_takes_value(self, action: Any) -> bool:
        return getattr(action, "nargs", None) != 0

    def _flag_accepts_multiple(self, action: Any) -> bool:
        return getattr(action, "nargs", None) in ("+", "*")

    def _get_command_description(self, cmd: Command) -> str:
        for attr in ("description", "help", "summary"):
            value = getattr(cmd, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        doc = getattr(cmd, "__doc__", None)
        if isinstance(doc, str) and doc.strip():
            return doc.strip().splitlines()[0]

        return ""

    def register_autocomplete(self, command: str, handler: Callable) -> None:
        self.autocomplete_registry[command] = handler

    # ==========================================================
    # Input parsing / dispatch
    # ==========================================================

    def handle_command(self, raw: str) -> None:
        command, args = self._parse_input(raw)
        if not command:
            return

        if command in ("exit", "quit"):
            self.application.exit()
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
            self.append_console(f"Error parsing input: {ve}")
            return None, []

    def _dispatch_command(self, command: str, args: list[str]) -> None:
        if command not in self.commands:
            self.logger.warning(f"Unknown command entered: '{command}'")
            self.append_console(f'Unknown command: "{command}". Type "help" for available commands.')
            return

        try:
            self.logger.info(f"Dispatching command: {command} (args={args})")

            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()

            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = self.commands[command].command(args)

            stdout_text = stdout_buffer.getvalue().strip()
            stderr_text = stderr_buffer.getvalue().strip()

            if stdout_text:
                self.append_console(stdout_text)

            if stderr_text:
                self.append_console(stderr_text)

            self._handle_command_result(result)

            self.logger.info(f"Command '{command}' executed successfully.")

        except Exception as e:
            self._handle_error(command, e)

    def _handle_command_result(self, result: Any) -> None:
        """
        Interpret a CommandResult and render it into the CLI panes.
        """

        if result is None:
            return

        # Normalize non-CommandResult responses
        if not isinstance(result, CommandResult):
            result = CommandResult.text(str(result))

        render_plan = self.result_renderer.render(result)

        console_text = render_plan["console_text"]
        side_text = render_plan["side_text"]
        side_title = render_plan["side_title"]
        replace_side_panel = render_plan["replace_side_panel"]

        if console_text:
            self.append_console(console_text)

        if side_text:
            if replace_side_panel:
                self.set_side_panel(side_text, title=side_title)
            else:
                self.append_side_panel(side_text, title=side_title)

    def _handle_error(self, context: str, exception: Exception) -> None:
        self.logger.error(f"[Error] {context} failed: {exception}", exc_info=True)
        self.append_console(f"[Error] {context}: {exception}")

    def _exit(self) -> None:
        self.logger.info("Exiting CLI.")
        self._cleanup()
        sys.exit(0)