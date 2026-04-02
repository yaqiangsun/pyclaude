"""
Debug logging utilities.

Provides debug logging with filtering support.
"""

import os
import sys
import logging
from typing import Optional, Any
from functools import lru_cache
from enum import Enum

logger = logging.getLogger(__name__)


class DebugLogLevel(Enum):
    """Debug log levels."""
    VERBOSE = "verbose"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


LEVEL_ORDER = {
    DebugLogLevel.VERBOSE: 0,
    DebugLogLevel.DEBUG: 1,
    DebugLogLevel.INFO: 2,
    DebugLogLevel.WARN: 3,
    DebugLogLevel.ERROR: 4,
}

# Runtime debug enabled flag
_runtime_debug_enabled = False


@lru_cache(maxsize=1)
def get_min_debug_log_level() -> DebugLogLevel:
    """Get minimum log level for debug output.

    Defaults to 'debug', which filters out 'verbose' messages.
    Set CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose to include high-volume diagnostics.
    """
    raw = os.environ.get("CLAUDE_CODE_DEBUG_LOG_LEVEL", "").lower().strip()
    if raw in ("verbose", "debug", "info", "warn", "error"):
        return DebugLogLevel(raw)
    return DebugLogLevel.DEBUG


def is_debug_mode() -> bool:
    """Check if debug mode is enabled.

    Returns:
        True if debug mode is active
    """
    global _runtime_debug_enabled

    if _runtime_debug_enabled:
        return True

    if os.environ.get("DEBUG") in ("1", "true", "yes", "on"):
        return True

    if os.environ.get("DEBUG_SDK") in ("1", "true", "yes", "on"):
        return True

    if "--debug" in sys.argv or "-d" in sys.argv:
        return True

    if any(arg.startswith("--debug=") for arg in sys.argv):
        return True

    if get_debug_file_path() is not None:
        return True

    return False


def enable_debug() -> None:
    """Enable debug logging mid-session."""
    global _runtime_debug_enabled
    _runtime_debug_enabled = True


def is_debug_to_stderr() -> bool:
    """Check if debug output should go to stderr.

    Returns:
        True if debug to stderr is enabled
    """
    return os.environ.get("DEBUG") is not None or "--debug" in sys.argv


def get_debug_file_path() -> Optional[str]:
    """Get debug log file path.

    Returns:
        Path to debug log file, or None
    """
    path = os.environ.get("CLAUDE_CODE_DEBUG_LOG_FILE")
    return path if path else None


def log_for_debugging(
    message: str,
    level: str = "debug",
    data: Optional[Any] = None,
) -> None:
    """Log a debug message.

    Args:
        message: Debug message
        level: Log level (debug, info, warn, error)
        data: Optional additional data to log
    """
    if not is_debug_mode():
        return

    min_level = get_min_debug_log_level()
    msg_level = DebugLogLevel(level) if level in LEVEL_ORDER else DebugLogLevel.DEBUG

    if LEVEL_ORDER[msg_level] < LEVEL_ORDER[min_level]:
        return

    if data:
        message = f"{message}: {data}"

    if msg_level == DebugLogLevel.ERROR:
        logger.error(message)
    elif msg_level == DebugLogLevel.WARN:
        logger.warning(message)
    elif msg_level == DebugLogLevel.INFO:
        logger.info(message)
    else:
        logger.debug(message)


__all__ = [
    "DebugLogLevel",
    "get_min_debug_log_level",
    "is_debug_mode",
    "enable_debug",
    "is_debug_to_stderr",
    "get_debug_file_path",
    "log_for_debugging",
]