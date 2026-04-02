"""
Binary check utility.

Check if a binary/command is installed and available on the system.
"""

import shutil
import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# Session cache to avoid repeated checks
_binary_cache: dict = {}


def is_binary_installed(command: str) -> bool:
    """Check if a binary/command is installed and available on the system.

    Uses 'which' on Unix systems (macOS, Linux, WSL) and 'where' on Windows.

    Args:
        command: The command name to check (e.g., 'gopls', 'rust-analyzer')

    Returns:
        True if the command exists, False otherwise
    """
    global _binary_cache

    # Edge case: empty or whitespace-only command
    if not command or not command.strip():
        logger.debug("[binaryCheck] Empty command provided, returning false")
        return False

    # Trim the command to handle whitespace
    trimmed_command = command.strip()

    # Check cache first
    if trimmed_command in _binary_cache:
        cached = _binary_cache[trimmed_command]
        logger.debug(f"[binaryCheck] Cache hit for '{trimmed_command}': {cached}")
        return cached

    # Check if command exists
    exists = shutil.which(trimmed_command) is not None

    # Cache the result
    _binary_cache[trimmed_command] = exists

    logger.debug(
        f"[binaryCheck] Binary '{trimmed_command}' {'found' if exists else 'not found'}"
    )

    return exists


def clear_binary_cache() -> None:
    """Clear the binary check cache (useful for testing)."""
    global _binary_cache
    _binary_cache.clear()


__all__ = ["is_binary_installed", "clear_binary_cache"]