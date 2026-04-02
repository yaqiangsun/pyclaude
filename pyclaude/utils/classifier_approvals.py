"""
Classifier approvals utilities.
"""

from typing import Optional, Dict, Any


# Approval states
APPROVAL_STATES = ["pending", "approved", "denied", "bypass"]


def check_classifier_approval(
    tool_name: str,
    command: str,
) -> Optional[str]:
    """Check if a command is approved by classifier.

    Args:
        tool_name: Tool name
        command: Command to check

    Returns:
        Approval state or None
    """
    return None


def get_classifier_approval_state(
    tool_name: str,
) -> Dict[str, Any]:
    """Get classifier approval state for a tool.

    Args:
        tool_name: Tool name

    Returns:
        Approval configuration
    """
    return {
        "auto_approve": False,
        "require_confirmation": True,
    }


def record_classifier_approval(
    tool_name: str,
    command: str,
    approved: bool,
) -> None:
    """Record classifier approval decision.

    Args:
        tool_name: Tool name
        command: Command that was approved/denied
        approved: Whether it was approved
    """
    pass


__all__ = [
    "APPROVAL_STATES",
    "check_classifier_approval",
    "get_classifier_approval_state",
    "record_classifier_approval",
]