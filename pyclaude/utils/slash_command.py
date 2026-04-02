"""
Slash command parsing utilities.

Parse slash commands.
"""

import re
from typing import Optional, Dict, Any, Tuple


# Slash command pattern
COMMAND_PATTERN = re.compile(r'^/(\w+)(?:\s+(.*))?$')


def parse_slash_command(text: str) -> Optional[Tuple[str, str]]:
    """Parse slash command.

    Args:
        text: Text to parse

    Returns:
        (command, args) or None
    """
    match = COMMAND_PATTERN.match(text.strip())
    if match:
        return (match.group(1), match.group(2) or "")
    return None


def is_slash_command(text: str) -> bool:
    """Check if text is a slash command.

    Args:
        text: Text to check

    Returns:
        True if slash command
    """
    return text.strip().startswith("/")


def get_command_help(command: str) -> Optional[str]:
    """Get help for command.

    Args:
        command: Command name

    Returns:
        Help text or None
    """
    help_texts = {
        "help": "Show help message",
        "quit": "Exit the application",
        "clear": "Clear the screen",
    }
    return help_texts.get(command)


__all__ = [
    "COMMAND_PATTERN",
    "parse_slash_command",
    "is_slash_command",
    "get_command_help",
]