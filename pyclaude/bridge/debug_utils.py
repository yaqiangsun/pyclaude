"""Bridge debug utilities."""

import os
import time
from typing import Any, Dict, Optional


DEBUG_MODE = os.environ.get('CLAUDE_BRIDGE_DEBUG', '').lower() == 'true'


def bridge_debuglog(message: str, **kwargs: Any) -> None:
    """Log debug message for bridge."""
    if not DEBUG_MODE:
        return

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    extra = ' '.join(f'{k}={v}' for k, v in kwargs.items()) if kwargs else ''
    print(f'[bridge] [{timestamp}] {message} {extra}')


def bridge_error(message: str, error: Optional[Exception] = None) -> None:
    """Log bridge error."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    error_msg = f' - {error}' if error else ''
    print(f'[bridge ERROR] [{timestamp}] {message}{error_msg}')


def log_for_debugging(message: str, **kwargs: Any) -> None:
    """Log message for debugging."""
    bridge_debuglog(message, **kwargs)


__all__ = ['DEBUG_MODE', 'bridge_debuglog', 'bridge_error', 'log_for_debugging']