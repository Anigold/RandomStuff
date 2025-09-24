# region ---- Imports ----

from backend.infra.logger import Logger

import shlex
import sys
from typing import Optional
from backend.infra.paths import CLI_HISTORY_FILE
import re
import time
try:
    import readline
except ImportError:
    import pyreadline3 as pry
    sys.modules['readline'] = pry
    import readline

# from backend.errors import (
#     WorkBotError,
#     CLIInputError,
#     VendorBotError,
#     SeleniumError,
#     VendorLoginError,
#     OrderError,
#     PricingError,
#     FileAccessError,
# )

# endregion

@Logger.attach_logger
class CLI:

    FLAG_REGEX_PATTERN = r'(--\w[\w-]*)(?:\s+([^\s-][^\s]*))?'

    # region ---- Initialization ----
    
    def __init__(self) -> None:

        self.logger.info('Initializing CLI.')

        self.commands = {}
        self._register_commands()

        self.autocomplete_registry = {}
        self._setup_autocomplete()

        self.logger.info(f'CLI initialized successfully with {len(self.commands)} commands.')

    # endregion
    
    # region ---- Command Registration ----
    
    def _register_commands(self) -> None:
        count = 0
        for function_name in dir(self):
            if function_name.startswith('cmd_'):
                command_name = function_name[4:]
                self.commands[command_name] = getattr(self, function_name)
                count += 1
        self.logger.debug(f'Registered {count} commands: {list(self.commands.keys())}')

    def _register_autocomplete(self) -> None:
        count = 0
        for function_name in dir(self):
            prefix = '_autocomplete_'
            if function_name.startswith(prefix):
                autocomplete_name = function_name[len(prefix):]
                self.autocomplete_registry[autocomplete_name] = getattr(self, function_name)
                count += 1
        self.logger.debug(f'Registered {count} autocomplete handlers.')
    
    # endregion

    # region ---- Autocomplete Setup ----

    def _setup_autocomplete(self) -> None:
        self.logger.debug("Setting up autocomplete and history.")
        readline.set_completer(self._completer)

        # Fix hyphen behavior in flag completion
        delimiters = readline.get_completer_delims().replace('-', '')
        readline.set_completer_delims(delimiters + ' ')

        # Readline behavior tuning
        readline.parse_and_bind('set completion-ignore-case on')
        readline.parse_and_bind('set show-all-if-ambiguous on')
        readline.parse_and_bind('set menu-complete-display-prefix on')
        readline.parse_and_bind('set skip-completed-text on')
        readline.parse_and_bind('TAB: complete')

        # History
        if CLI_HISTORY_FILE.exists():
            readline.read_history_file(str(CLI_HISTORY_FILE))
            self.logger.info(f"Loaded command history from {str(CLI_HISTORY_FILE)}")

        readline.set_history_length(100)
        self._register_autocomplete()

    # endregion

    # region ---- Autocompletion Core ----
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        '''Autocompletion entry point registered with readline.

        This method is invoked repeatedly by the readline library during TAB completion.
        It is responsible for returning the nth matching completion for the given `text`.

        Parameters:
            text (str): The current word fragment that the user is attempting to complete.
                        This is determined by readline and is the portion of the buffer
                        from the most recent delimiter up to the cursor.
            state (int): The match index being requested by readline. On the first call,
                        state == 0. Subsequent calls (e.g. if multiple matches exist)
                        will increment state and expect the next possible match.

        Returns:
            Optional[str]: The `state`-th matching completion string if available;
                        otherwise, None to signal no more matches.

        Completion Logic:
        -----------------
        1. If the input buffer is empty, suggest all registered commands.
        2. If the input buffer has only one word fragment (no space yet), suggest commands that match the input prefix.
        3. If the buffer contains a command and flags/arguments:
        - Delegate to `_complete_arguments()` to determine whether to suggest:
            - Valid flags for the given command
            - Values for the current flag based on context
            - Nothing if context is ambiguous or invalid

        Internally Uses:
        ----------------
        - `readline.get_line_buffer()` to access the full input buffer
        - `_complete_commands()` for top-level command name suggestions
        - `_complete_arguments()` for argument-level parsing and completion

        Example:
            Input:  'download_orders --sto'
            text:   '--sto'
            state:  0 → returns '--stores'
            state:  1 → returns None (if no more matches)

        Integration:
            This method is registered once via `readline.set_completer(self._completer)`
            during CLI initialization.

        Notes:
            - This function must be side-effect free.
            - It must not modify internal state.
            - It should execute quickly since it's called repeatedly per TAB press.
        '''

        buffer = readline.get_line_buffer().strip()

        if not buffer:
            options = self._complete_commands(text)
        elif ' ' not in buffer:
            options = self._complete_commands(text)
        else:
            options = self._complete_arguments(buffer, text)

        return options[state] if state < len(options) else None

    def _complete_commands(self, text: str) -> list[str]:
        return [cmd for cmd in self.commands.keys() if cmd.startswith(text)]

    def _complete_arguments(self, buffer: str, text: str) -> list[str]:
        '''Determines context-aware autocompletion suggestions for a given command buffer.

        This method is invoked by `_completer()` when the user has typed beyond a single command.
        It attempts to infer whether the user is typing a flag or a flag's argument, and routes
        the query accordingly.

        Parameters:
            buffer (str): The full raw input line from the user, as retrieved from `readline`.
                        Example: 'download_orders --stores 'Dow'
            text (str):   The current word fragment under the cursor. Typically the word being typed
                        (e.g., 'Dow', '--ven', etc.) and used to match completions.

        Returns:
            list[str]: A list of string completions that match the inferred context, suitable
                    for feeding back to the readline `completer()` function.

        Completion Cases Handled:
        --------------------------
        1. Typing a flag (e.g., '--ven' → suggests `--vendors`)
        2. Typing a value for a known flag (e.g., `--stores 'Dow` → suggests `Downtown`)
        3. Typing inside a partially-quoted flag value
        4. Single flag position after command (fallback case)
        5. Fallback to empty list when context is not understood or ambiguous

        Behavior:
        ---------
        - Tries to split the buffer using `shlex.split()` to preserve quoted values.
        - Falls back to a basic `split()` if quotes are incomplete or invalid.
        - Uses regex to extract previously typed flags from the buffer.
        - Resolves the most recent valid flag using `_get_last_valid_flag()`.
        - Delegates value suggestions to `_get_autocomplete_values()` if appropriate.

        Example:
            buffer = 'download_orders --stores 'Dow'
            text   = 'Dow'
            returns → ['Downtown']

        Performance:
            Fast and stateless; avoids mutation and heavy parsing.
        '''
        
        tokens = None
        try:
            tokens = shlex.split(buffer)
        except ValueError:
            tokens = buffer.split()
    
        if not tokens:
            return []

        command = tokens[0]
        if command not in self.commands:
            return []

        possible_flags = self._get_command_flags(command)
        matches = re.findall(self.FLAG_REGEX_PATTERN, buffer)

        last_token = tokens[-1] if tokens else ''
        last_token_stripped = last_token.strip(''').strip(''')
        last_flag = self._get_last_valid_flag(matches, possible_flags)
        
        # Case 1: Typing or completing a flag
        if last_token.startswith('--') or (buffer.endswith(' ') and not last_flag):
            return [f for f in possible_flags if f.startswith(text)]

        # Case 2: After a complete flag, expecting a value
        elif last_flag and (last_token == last_flag or buffer.endswith(' ')):
            self.logger.info(f'{command}, {last_flag}, {text}')
            return self._get_autocomplete_values(command, last_flag, text)

        # Case 3: Inside a value for a known flag
        elif last_flag and (last_token_stripped not in possible_flags):
            self.logger.info(f'{command}, {last_flag}, {text}')
            return self._get_autocomplete_values(command, last_flag, text)

        # Case 4: First argument after command
        elif len(tokens) == 2:
            return [f for f in possible_flags if f.startswith(text)]

        return []

    def _get_last_valid_flag(self, matches: list[tuple], possible_flags: list[str]) -> Optional[str]:
        for flag, _ in reversed(matches):
            if flag in possible_flags:
                return flag
        return None

    def _get_autocomplete_values(self, command: str, flag: str, text: str) -> list[str]:
        '''Invokes the appropriate autocomplete handler for a given command and flag.

        This method is responsible for routing value completions (e.g. store names,
        vendor names) to the correct handler defined by the subclass (e.g. `_autocomplete_download_orders`).

        Parameters:
            command (str): The command being executed (e.g. 'download_orders').
            flag (str):    The specific flag for which the value is being completed (e.g. '--stores').
            text (str):    The partially typed value to match against (e.g. 'Dow').

        Returns:
            list[str]: A list of strings representing possible completions for the given flag.

        Quoted Value Handling:
        ----------------------
        - If `text` appears to be quoted (e.g., ''Dow'), it is unwrapped before being passed to the handler.
        - Returned completions will be re-wrapped in matching quotes to preserve shell safety.

        Assumptions:
        ------------
        - A corresponding `_autocomplete_<command>()` handler exists and is registered
        in `self.autocomplete_registry[command]`.
        - The handler accepts `(flag: str, text: str)` and returns a list of strings.

        Example Handler Signature:
            def _autocomplete_download_orders(self, flag: str, text: str) -> list[str]:
                if flag == '--stores':
                    return [s for s in ['Downtown', 'Collegetown'] if s.startswith(text)]

        Example:
            _get_autocomplete_values('download_orders', '--stores', 'Dow')
            → ['Downtown']

        Returns an empty list if no handler is found or an error occurs.
        '''
        
        if command in self.autocomplete_registry:
            handler = self.autocomplete_registry[command]

            is_quoted = text.startswith((''', '''))
            stripped = text.strip(''').strip(''')

            completions = handler(flag, stripped)

            if is_quoted:
                quote = text[0]
                return [f'{quote}{match}{quote}' for match in completions]

            return completions

        return []

    def _get_command_flags(self, command: str) -> list[str]:
        if hasattr(self, f'args_{command}'):
            parser = getattr(self, f'args_{command}')()
            return list(parser._option_string_actions.keys())
        return []

    def register_autocomplete(self, command: str, handler):
        self.autocomplete_registry[command] = handler

    # endregion

    # region ---- CLI Loop ----
    
    def start(self, welcome_screen: str = '\nWelcome to your CLI. Type "help" to see available commands.\n') -> None:
        self.logger.info('CLI session started.')
        print(welcome_screen)
        self._run()

    def _run(self):
        prompt = 'WorkBot> '

        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    continue

                self.logger.debug(f"User input received: {user_input}")

                command, args = self._parse_input(user_input)
                if not command:
                    continue

                if command in ('exit', 'quit'):
                    self.logger.info("User requested CLI shutdown.")
                    break

                self._dispatch_command(command, args)

            except (KeyboardInterrupt, EOFError):
                self.logger.info("CLI interrupted by user (Ctrl+C / EOF).")
                print('\nExiting CLI.')
                break

            finally:
                self._persist_history()

        self._exit()

    # endregion

    # region ---- Utility Commands ----
    
    def cmd_shutdown(self):
        '''Shuts down CLI.'''
        self.logger.info("Shutdown command invoked.")
        self._cleanup()
        self._exit()

    def cmd_help(self) -> None:
        '''Displays available commands'''
        self.logger.info("Help command invoked.")
        print('\nAvailable Commands:')
        for command in sorted(self.commands.keys()):
            print(f'  {command}')
        print('\nType "command --help" for more details.\n')

    def cmd_clear_history(self) -> None:
        self.logger.info("Clear history command invoked.")
        try:
            open(CLI_HISTORY_FILE, 'w').close()
            readline.clear_history()
            print('Command history cleared.')
        except Exception as e:
            print(f'Error: Failed to clear history ({e})')

    def _cleanup(self) -> None:
        '''Performs any necessary cleanup before exiting.'''
        # Placeholder for any cleanup logic (e.g., closing files, releasing resources)
        # Overwrite for functionality.  
        pass

    def _exit(self) -> None:
        self.logger.info("Exiting CLI and saving history.")
        try:
            readline.write_history_file(str(CLI_HISTORY_FILE))
            self.logger.debug(f"History saved to {str(CLI_HISTORY_FILE)}")
        except Exception as e:
            self.logger.warning(f"Failed to save history: {e}")
            print(f'Warning: Failed to save history ({e})')
        time.sleep(1)
        sys.exit(0)

    def _parse_input(self, user_input: str) -> tuple[Optional[str], list[str]]:
        try:
            args = shlex.split(user_input)
            command, params = args[0], args[1:]
            self.logger.debug(f"Parsed command='{command}', args={params}")
            return command, params
        except ValueError as ve:
            self.logger.error(f"Failed to parse input '{user_input}': {ve}")
            print(f'Error parsing input: {ve}')
            return None, []
        
    def _dispatch_command(self, command: str, args: list[str]) -> None:
        
        if command not in self.commands:
            self.logger.warning(f"Unknown command entered: '{command}'")
            print(f'Unknown command: "{command}". Type "help" for available commands.')
            return

        try:
            self.logger.info(f"Dispatching command: {command} (args={args})")
            self.commands[command](args) if args else self.commands[command]()
            self.logger.info(f"Command '{command}' executed successfully.")
        except Exception as e:
            self._handle_error(command, e)

    def _handle_error(self, context: str, exception: Exception) -> None:
        self.logger.error(f"[Error] {context} failed: {exception}", exc_info=True)
        print(f'[Error] {context}: {exception}')
        # Optionally log to file or stderr
        # self.logger.error(f'{context} failed: {exception}')

    def _persist_history(self) -> None:
        try:
            readline.write_history_file(str(CLI_HISTORY_FILE))
            self.logger.debug("Persisted command history to file.")
        except Exception as e:
            self._handle_error('History Save', e)
        
    # endregion