"""
Sanitization utilities.

Data sanitization for logging/output.
"""

import re
from typing import Optional


def sanitize_path(path: str) -> str:
    """Sanitize file path for display.

    Args:
        path: File path

    Returns:
        Sanitized path
    """
    # Replace home directory with ~
    import os
    home = os.path.expanduser("~")
    if path.startswith(home):
        return "~" + path[len(home):]
    return path


def sanitize_for_logging(text: str, sensitive_patterns: Optional[list] = None) -> str:
    """Sanitize text for logging.

    Args:
        text: Text to sanitize
        sensitive_patterns: Regex patterns for sensitive data

    Returns:
        Sanitized text
    """
    if sensitive_patterns is None:
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',  # Credit card
            r'api[_-]?key["\s:=]+["\']?[\w-]+["\']?',  # API keys
        ]

    result = text
    for pattern in sensitive_patterns:
        result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)

    return result


def sanitize_command_args(args: list) -> list:
    """Sanitize command arguments.

    Args:
        args: Command arguments

    Returns:
        Sanitized arguments
    """
    sensitive = ["--password", "--api-key", "--token", "-p"]
    result = []
    skip_next = False

    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            result.append("[REDACTED]")
            continue

        if arg in sensitive:
            skip_next = True
            result.append(arg)
        else:
            result.append(arg)

    return result


__all__ = [
    "sanitize_path",
    "sanitize_for_logging",
    "sanitize_command_args",
]