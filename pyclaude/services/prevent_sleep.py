"""
Prevent sleep service - keeps the system awake when needed.
"""
import os
import subprocess
from typing import Optional


# Track if prevent sleep is active
_prevent_sleep_active = False


def is_prevent_sleep_active() -> bool:
    """Check if prevent sleep is currently active."""
    global _prevent_sleep_active
    return _prevent_sleep_active


async def prevent_sleep(reason: str = "Claude Code is running") -> bool:
    """
    Prevent the system from sleeping.

    Args:
        reason: Reason for preventing sleep

    Returns:
        True if successful
    """
    global _prevent_sleep_active

    if os.environ.get('USER_TYPE') == 'ant':
        # On devboxes, use logind or systemd-inhibit
        try:
            # Try to inhibit sleep using systemd
            subprocess.Popen(
                ['systemd-inhibit', '--why', reason, 'sleep', '30'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _prevent_sleep_active = True
            return True
        except Exception:
            pass

    # On macOS, use caffeinate
    if os.environ.get('TERM_PROGRAM') == 'Apple_Terminal' or os.uname().sysname == 'Darwin':
        try:
            subprocess.Popen(
                ['caffeinate', '-d', '-i', '-s'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            _prevent_sleep_active = True
            return True
        except Exception:
            pass

    return False


async def allow_sleep() -> None:
    """Allow the system to sleep again."""
    global _prevent_sleep_active
    _prevent_sleep_active = False
    # The caffeinate process will terminate when the parent exits


__all__ = ['prevent_sleep', 'allow_sleep', 'is_prevent_sleep_active']