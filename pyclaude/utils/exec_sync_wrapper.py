"""
Exec sync wrapper.

DEPRECATED: Use async alternatives when possible. Sync exec calls block the event loop.

Wrapped execSync with slow operation logging.
"""

import subprocess
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


# Placeholder for slow logging - replace with actual implementation when available
def slow_logging(*args: Any) -> Any:
    """Template tag placeholder for slow operation logging."""
    return args


def exec_sync(command: str, options: Optional[dict] = None) -> Any:
    """Execute a command synchronously (DEPRECATED).

    Use async alternatives when possible.

    Args:
        command: The command to execute
        options: Optional execution options

    Returns:
        Command output
    """
    with slow_logging(f"execSync: {command[:100]}"):
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=options.get("encoding") == "utf8" if options else False,
        )
        if options and options.get("encoding") == "utf8":
            return result.stdout
        return result.stdout.encode() if result.stdout else b""


# Alias for backwards compatibility
exec_sync_deprecated = exec_sync


__all__ = ["exec_sync", "exec_sync_deprecated"]