"""
Activity manager for tracking user and CLI operations.

Provides activity tracking with automatic deduplication of overlapping activities.
"""

from typing import Optional, Callable, Awaitable, Set, Dict, Any
from dataclasses import dataclass, field
import time


# Type alias for the active time counter function
GetActiveTimeCounter = Callable[[], Optional[Any]]


@dataclass
class ActivityManager:
    """Handles generic activity tracking for user and CLI operations."""

    active_operations: Set[str] = field(default_factory=set)
    last_user_activity_time: float = 0
    last_cli_recorded_time: float = field(default_factory=lambda: time.time() * 1000)
    is_cli_active: bool = False

    USER_ACTIVITY_TIMEOUT_MS: int = 5000  # 5 seconds

    get_now: Callable[[], float] = field(default_factory=lambda: lambda: time.time() * 1000)
    get_active_time_counter: GetActiveTimeCounter = field(default_factory=lambda: lambda: None)

    _instance: Optional["ActivityManager"] = None

    def __post_init__(self):
        self.last_cli_recorded_time = self.get_now()

    @classmethod
    def get_instance(cls) -> "ActivityManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None

    @classmethod
    def create_instance(cls, options: Optional[Dict[str, Any]] = None) -> "ActivityManager":
        """Create a new instance with custom options (for testing)."""
        instance = cls()
        if options:
            if "get_now" in options:
                instance.get_now = options["get_now"]
            if "get_active_time_counter" in options:
                instance.get_active_time_counter = options["get_active_time_counter"]
        cls._instance = instance
        return instance

    def record_user_activity(self) -> None:
        """Called when user interacts with the CLI."""
        if not self.is_cli_active and self.last_user_activity_time != 0:
            now = self.get_now()
            time_since_last_activity = (now - self.last_user_activity_time) / 1000

            if time_since_last_activity > 0:
                active_time_counter = self.get_active_time_counter()
                if active_time_counter:
                    timeout_seconds = self.USER_ACTIVITY_TIMEOUT_MS / 1000

                    if time_since_last_activity < timeout_seconds:
                        active_time_counter.add(time_since_last_activity, {"type": "user"})

        # Update the last user activity timestamp
        self.last_user_activity_time = self.get_now()

    def start_cli_activity(self, operation_id: str) -> None:
        """Start tracking CLI activity."""
        # If operation already exists, force cleanup
        if operation_id in self.active_operations:
            self.end_cli_activity(operation_id)

        was_empty = len(self.active_operations) == 0
        self.active_operations.add(operation_id)

        if was_empty:
            self.is_cli_active = True
            self.last_cli_recorded_time = self.get_now()

    def end_cli_activity(self, operation_id: str) -> None:
        """Stop tracking CLI activity."""
        self.active_operations.discard(operation_id)

        if len(self.active_operations) == 0:
            now = self.get_now()
            time_since_last_record = (now - self.last_cli_recorded_time) / 1000

            if time_since_last_record > 0:
                active_time_counter = self.get_active_time_counter()
                if active_time_counter:
                    active_time_counter.add(time_since_last_record, {"type": "cli"})

            self.last_cli_recorded_time = now
            self.is_cli_active = False

    async def track_operation(
        self,
        operation_id: str,
        fn: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Track an async operation automatically."""
        self.start_cli_activity(operation_id)
        try:
            return await fn()
        finally:
            self.end_cli_activity(operation_id)

    def get_activity_states(self) -> Dict[str, Any]:
        """Get current activity states."""
        now = self.get_now()
        time_since_user_activity = (now - self.last_user_activity_time) / 1000
        is_user_active = time_since_user_activity < self.USER_ACTIVITY_TIMEOUT_MS / 1000

        return {
            "isUserActive": is_user_active,
            "isCLIActive": self.is_cli_active,
            "activeOperationCount": len(self.active_operations),
        }


# Export singleton instance
activity_manager = ActivityManager.get_instance()


__all__ = [
    "ActivityManager",
    "activity_manager",
]