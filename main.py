"""
main.py — Entry point for the effective-system agent CLI.

Usage
-----
    python main.py          # start interactive REPL
    python main.py /_learn  # jump straight to the trading tour

Commands
--------
    /_learn   Start (or resume) the interactive trading tour.
    /help     Show available commands.
    /quit     Exit the REPL.
"""

from __future__ import annotations

import sys

from agent.graph import TourContext
from agent.trading_tour import run_tour


HELP_TEXT = """\
Available commands
──────────────────
  /_learn   — Start the interactive trading tour
  /help     — Show this help
  /quit     — Exit
"""


def _handle_command(cmd: str) -> bool:
    """
    Handle a single command string.
    Returns True if the REPL should keep running, False to exit.
    """
    cmd = cmd.strip()

    if cmd in ("/quit", "/exit", "quit", "exit"):
        print("Goodbye!")
        return False

    if cmd == "/help":
        print(HELP_TEXT)
        return True

    if cmd == "/_learn":
        run_tour()
        return True

    if cmd.startswith("/"):
        print(f"Unknown command '{cmd}'.  Type /help for available commands.")
        return True

    # Plain text — echo a prompt for now (extend with LLM later)
    print("ℹ️  Type /_learn to start the trading tour, or /help for commands.")
    return True


def main() -> None:
    # Allow `python main.py /_learn` as a shortcut
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        _handle_command(cmd)
        return

    print("effective-system agent  •  type /help for commands\n")
    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not line:
            continue
        if not _handle_command(line):
            break


if __name__ == "__main__":
    main()
