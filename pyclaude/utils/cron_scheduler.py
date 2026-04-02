"""
Cron scheduler utilities.

Manages scheduled tasks using cron expressions.
"""

import asyncio
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime
from .cron import parse_cron, get_next_run, CronFields


@dataclass
class ScheduledTask:
    """A scheduled task."""
    id: str
    cron_expression: str
    handler: Callable
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class CronScheduler:
    """Cron-based task scheduler."""

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False

    def schedule(
        self,
        task_id: str,
        cron_expression: str,
        handler: Callable,
    ) -> None:
        """Schedule a task.

        Args:
            task_id: Unique task identifier
            cron_expression: Cron expression
            handler: Async function to run
        """
        cron_fields = parse_cron(cron_expression)
        if not cron_fields:
            raise ValueError(f"Invalid cron expression: {cron_expression}")

        next_run = get_next_run(cron_fields)
        self.tasks[task_id] = ScheduledTask(
            id=task_id,
            cron_expression=cron_expression,
            handler=handler,
            next_run=next_run,
        )

    def unschedule(self, task_id: str) -> None:
        """Remove a scheduled task.

        Args:
            task_id: Task identifier
        """
        self.tasks.pop(task_id, None)

    def enable(self, task_id: str) -> None:
        """Enable a task.

        Args:
            task_id: Task identifier
        """
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True

    def disable(self, task_id: str) -> None:
        """Disable a task.

        Args:
            task_id: Task identifier
        """
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False

    async def start(self) -> None:
        """Start the scheduler."""
        self._running = True
        while self._running:
            await asyncio.sleep(60)  # Check every minute

    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False


# Global scheduler instance
_scheduler = CronScheduler()


def get_scheduler() -> CronScheduler:
    """Get the global scheduler."""
    return _scheduler


__all__ = [
    "ScheduledTask",
    "CronScheduler",
    "get_scheduler",
]