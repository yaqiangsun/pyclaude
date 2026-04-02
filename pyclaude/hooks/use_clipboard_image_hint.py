"""
Use clipboard image hint hook.

Shows a notification when the terminal regains focus and the clipboard
contains an image.
"""

import time
from typing import Optional, Callable

NOTIFICATION_KEY = "clipboard-image-hint"
# Small debounce to batch rapid focus changes
FOCUS_CHECK_DEBOUNCE_MS = 1000
# Don't show the hint more than once per this interval
HINT_COOLDOWN_MS = 30000

# State
_last_focused = False
_last_hint_time = 0
_check_timeout = None


def has_image_in_clipboard() -> bool:
    """Check if clipboard has an image."""
    # Placeholder - would use actual clipboard check
    return False


def get_shortcut_display(shortcut: str, context: str, fallback: str) -> str:
    """Get shortcut display string."""
    return fallback


async def check_clipboard_and_notify(
    is_focused: bool,
    enabled: bool,
    add_notification: Optional[Callable] = None,
) -> None:
    """Check clipboard for image and show notification if needed.

    Args:
        is_focused: Whether the terminal is focused
        enabled: Whether image paste is enabled
        add_notification: Callback to add notification
    """
    global _last_focused, _last_hint_time

    if not enabled or not is_focused:
        _last_focused = is_focused
        return

    # Only trigger on focus regain (was unfocused, now focused)
    was_focused = _last_focused
    _last_focused = is_focused

    if was_focused:
        return

    # Check cooldown
    now = int(time.time() * 1000)
    if now - _last_hint_time < HINT_COOLDOWN_MS:
        return

    # Check if clipboard has an image
    if has_image_in_clipboard():
        _last_hint_time = now
        if add_notification:
            add_notification(
                key=NOTIFICATION_KEY,
                text=f"Image in clipboard · {get_shortcut_display('chat:imagePaste', 'Chat', 'ctrl+v')} to paste",
                priority="immediate",
                timeout_ms=8000,
            )


__all__ = ["check_clipboard_and_notify"]