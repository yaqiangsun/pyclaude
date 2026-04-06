"""
Notification service for sending system notifications.
"""
import os
import subprocess
from typing import Optional, Protocol, Any, Dict
from dataclasses import dataclass


class TerminalNotification(Protocol):
    """Protocol for terminal notification capabilities."""

    def notify_iterm2(self, opts: 'NotificationOptions') -> None: ...
    def notify_kitty(self, opts: Dict[str, Any]) -> None: ...
    def notify_ghostty(self, opts: Dict[str, Any]) -> None: ...
    def notify_bell(self) -> None: ...


@dataclass
class NotificationOptions:
    """Options for notification."""
    message: str
    title: Optional[str] = None
    notification_type: str = "default"


DEFAULT_TITLE = "Claude Code"


def get_terminal() -> str:
    """Get the current terminal type."""
    return os.environ.get('TERM', '')


def get_preferred_channel() -> str:
    """Get the preferred notification channel from config."""
    # Would load from global config in full implementation
    return os.environ.get('CLAUDE_NOTIFICATION_CHANNEL', 'auto')


async def send_notification(
    notif: NotificationOptions,
    terminal: Optional[TerminalNotification] = None,
) -> str:
    """
    Send a notification through the preferred channel.

    Args:
        notif: Notification options
        terminal: Terminal notification interface

    Returns:
        The method used for sending
    """
    channel = get_preferred_channel()
    method = await send_to_channel(channel, notif, terminal)
    return method


async def send_to_channel(
    channel: str,
    opts: NotificationOptions,
    terminal: Optional[TerminalNotification] = None,
) -> str:
    """Send notification to a specific channel."""
    title = opts.title or DEFAULT_TITLE

    try:
        if channel == 'auto':
            return await send_auto(opts, terminal)
        elif channel == 'iterm2':
            if terminal:
                terminal.notify_iterm2(opts)
            return 'iterm2'
        elif channel == 'iterm2_with_bell':
            if terminal:
                terminal.notify_iterm2(opts)
                terminal.notify_bell()
            return 'iterm2_with_bell'
        elif channel == 'kitty':
            if terminal:
                terminal.notify_kitty({'message': opts.message, 'title': title})
            return 'kitty'
        elif channel == 'ghostty':
            if terminal:
                terminal.notify_ghostty({'message': opts.message, 'title': title})
            return 'ghostty'
        elif channel == 'terminal_bell':
            if terminal:
                terminal.notify_bell()
            return 'terminal_bell'
        elif channel == 'notifications_disabled':
            return 'disabled'
        else:
            return 'none'
    except Exception:
        return 'error'


async def send_auto(
    opts: NotificationOptions,
    terminal: Optional[TerminalNotification] = None,
) -> str:
    """Auto-detect the best notification method based on terminal."""
    title = opts.title or DEFAULT_TITLE
    term = get_terminal()

    if term == 'Apple_Terminal':
        bell_disabled = await is_apple_terminal_bell_disabled()
        if bell_disabled:
            if terminal:
                terminal.notify_bell()
            return 'terminal_bell'
        return 'no_method_available'
    elif 'iTerm' in term:
        if terminal:
            terminal.notify_iterm2(opts)
        return 'iterm2'
    elif term == 'kitty':
        if terminal:
            terminal.notify_kitty({'message': opts.message, 'title': title})
        return 'kitty'
    elif term == 'ghostty':
        if terminal:
            terminal.notify_ghostty({'message': opts.message, 'title': title})
        return 'ghostty'
    else:
        return 'no_method_available'


def generate_kitty_id() -> int:
    """Generate a random ID for kitty notifications."""
    import random
    return random.randint(0, 9999)


async def is_apple_terminal_bell_disabled() -> bool:
    """Check if Apple Terminal bell is disabled."""
    if get_terminal() != 'Apple_Terminal':
        return False

    try:
        # Get current profile
        result = subprocess.run(
            ['osascript', '-e', 'tell application "Terminal" to name of current settings of front window'],
            capture_output=True,
            text=True,
            timeout=5
        )
        current_profile = result.stdout.strip()

        if not current_profile:
            return False

        # Check defaults
        defaults_result = subprocess.run(
            ['defaults', 'export', 'com.apple.Terminal', '-'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if defaults_result.returncode != 0:
            return False

        # Simple check - in full implementation would parse plist
        return 'Bell' in defaults_result.stdout and 'false' in defaults_result.stdout.lower()

    except Exception:
        return False


__all__ = ['send_notification', 'NotificationOptions', 'TerminalNotification']