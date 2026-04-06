"""Notifications context."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    """A notification."""
    id: str
    title: str
    message: str
    level: str = 'info'  # info, warning, error, success
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    actions: List[str] = field(default_factory=list)


class NotificationsContext:
    """Context for managing notifications."""

    def __init__(self):
        self._notifications: List[Notification] = []
        self._callback: Optional[Callable] = None

    def add_notification(self, notification: Notification) -> None:
        """Add a notification."""
        self._notifications.append(notification)
        if self._callback:
            self._callback(notification)

    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """Get notifications."""
        if unread_only:
            return [n for n in self._notifications if not n.read]
        return list(self._notifications)

    def mark_read(self, notification_id: str) -> None:
        """Mark a notification as read."""
        for n in self._notifications:
            if n.id == n.id:
                n.read = True

    def clear(self) -> None:
        """Clear all notifications."""
        self._notifications.clear()

    def set_callback(self, callback: Callable) -> None:
        """Set notification callback."""
        self._callback = callback


# Global context
_notifications_context = NotificationsContext()


def get_notifications_context() -> NotificationsContext:
    """Get the global notifications context."""
    return _notifications_context


__all__ = ['Notification', 'NotificationsContext', 'get_notifications_context']