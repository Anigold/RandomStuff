from ..command import Command
import argparse
import inspect
import textwrap
import itertools

class Help(Command):
    """
    Display help for all available CLI commands.

    Usage:
        help                     # list all commands with a short description
        help <command_name>      # show detailed help for a specific command
    """

    name = 'help'

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog="help",
            description="Show help for all commands or one specific command."
        )
        parser.add_argument("command", nargs="?", help="Name of the command to inspect.")
        return parser

    def autocomplete(self, flag: str, text: str):
        """Suggest command names for autocompletion."""
        return [name for name in self.context.cli.commands.keys() if name.startswith(text)]

    def command(self, args):
        cli = self.context.cli
        parser = self.arguments()
        parsed = parser.parse_args(args or [])

        if parsed.command:
            self._print_command_help(cli, parsed.command)
        else:
            self._print_all_commands(cli)

    def _print_command_help(self, cli, command_name: str):
        """Print detailed help for a single command."""
        target = cli.commands.get(command_name)
        if not target:
            print(f"\n[Error] Unknown command: '{command_name}'")
            return

        print(f"\nCommand: {command_name}")
        print("-" * (9 + len(command_name)))

        try:
            arg_parser = target.arguments()
            desc = textwrap.dedent(arg_parser.description or "No description provided.")
            print(desc + "\n")
            arg_parser.print_help()
        except Exception as e:
            print(f"[Error] Could not retrieve argument info for '{command_name}': {e}")

    def _print_all_commands(self, cli):
        """List all commands, grouped by origin (builtin / workbot / other)."""
        print("\nAvailable Commands:")
        print("-------------------")

        entries = self._collect_command_entries(cli)
        grouped = self._group_commands(entries)

        for group_name, group_entries in grouped.items():
            self._print_command_group(group_name, group_entries)

        print('\nType "help <command>" for detailed help on a specific command.\n')

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------
    def _collect_command_entries(self, cli) -> list[tuple[str, str, str]]:
        """Return list of (group, name, description) tuples for all commands."""
        entries = []
        for name, cmd in cli.commands.items():
            desc = self._get_command_description(cmd)
            group = self._infer_command_group(cmd)
            entries.append((group, name, desc))
        return sorted(entries, key=lambda x: (x[0], x[1]))

    def _get_command_description(self, cmd) -> str:
        """Extract a command's description (prefer parser description)."""
        try:
            parser = cmd.arguments()
            desc = parser.description or ""
        except Exception:
            doc = (cmd.__class__.__doc__ or "").strip()
            desc = doc.split("\n", 1)[0] if doc else ""
        return textwrap.shorten(desc, width=80, placeholder="...")

    def _infer_command_group(self, cmd) -> str:
        """Determine a command's group name based on its module path."""
        module_path = cmd.__class__.__module__
        if ".builtin" in module_path:
            return "Built-in Commands"
        elif ".workbot" in module_path:
            return "WorkBot Commands"
        else:
            return "Other Commands"

    def _group_commands(self, entries: list[tuple[str, str, str]]):
        """Return a dictionary: {group_name: [(name, desc), ...]}."""
        grouped = {}
        for group, group_items in itertools.groupby(entries, key=lambda x: x[0]):
            grouped[group] = [(name, desc) for _, name, desc in list(group_items)]
        return grouped

    def _print_command_group(self, group_name: str, group_entries: list[tuple[str, str]]):
        """Print a formatted list of commands in a specific group."""
        print(f"\n{group_name}:")
        print("-" * len(group_name))

        max_len = max(len(name) for name, _ in group_entries)
        padding = max(24, max_len + 2)

        for name, desc in group_entries:
            print(f"  {name.ljust(padding)}{desc}")
