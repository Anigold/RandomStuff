from __future__ import annotations

import sys

from apps.cli.cli import CLI

def main() -> int:
    try:
        cli = CLI()
        cli.start(
            welcome_screen=(
                "\n"
                "WorkBot CLI\n"
                'Type "help" to see available commands.\n'
            )
        )
        return 0

    except KeyboardInterrupt:
        return 0

    except Exception as exc:
        print(f"[Error] Failed to start WorkBot CLI: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())