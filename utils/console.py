"""
AccessOps Toolkit - Console Helpers
-----------------------------------
Shared console formatting and helper utilities.
"""

import sys


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def color_text(text: str, color: str) -> str:
    """Apply ANSI color formatting."""
    return f"{color}{text}{Colors.END}"


def success(text: str) -> str:
    return color_text(text, Colors.GREEN)


def warning(text: str) -> str:
    return color_text(text, Colors.YELLOW)


def error(text: str) -> str:
    return color_text(text, Colors.RED)


def info(text: str) -> str:
    return color_text(text, Colors.BLUE)


def header(text: str) -> str:
    return color_text(text, Colors.HEADER)


def bold(text: str) -> str:
    return color_text(text, Colors.BOLD)


def stderr(*message):
    """Print to stderr."""
    print(*message, file=sys.stderr)


def yes_no_prompt(message: str, default: str = "n") -> bool:
    """
    Interactive yes/no prompt.

    Returns:
        bool
    """
    valid = {
        "yes": True,
        "y": True,
        "no": False,
        "n": False,
    }

    while True:
        response = input(f"{message} (y/n) [{default}]: ").strip().lower()

        if not response:
            return valid[default]

        if response in valid:
            return valid[response]

        print(error("Invalid response. Use y/n."))


def required_input(message: str) -> str:
    """Force non-empty user input."""
    while True:
        result = input(message).strip()

        if result:
            return result

        print(error("Value required."))