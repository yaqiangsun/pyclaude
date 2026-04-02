"""
Workload context utilities.

Manage workload context across operations.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from contextvars import ContextVar


@dataclass
class WorkloadContext:
    """Workload context data."""
    workload_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# Context variable for current workload
_current_workload: ContextVar[Optional[WorkloadContext]] = ContextVar(
    'current_workload',
    default=None
)


def set_workload_context(context: Optional[WorkloadContext]) -> None:
    """Set current workload context.

    Args:
        context: Workload context
    """
    _current_workload.set(context)


def get_workload_context() -> Optional[WorkloadContext]:
    """Get current workload context.

    Returns:
        Current context or None
    """
    return _current_workload.get()


def clear_workload_context() -> None:
    """Clear current workload context."""
    _current_workload.set(None)


def get_workload_id() -> Optional[str]:
    """Get current workload ID.

    Returns:
        Workload ID or None
    """
    context = get_workload_context()
    return context.workload_id if context else None


__all__ = [
    "WorkloadContext",
    "set_workload_context",
    "get_workload_context",
    "clear_workload_context",
    "get_workload_id",
]