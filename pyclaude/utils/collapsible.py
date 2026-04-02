"""
Collapsible sections utilities.
"""

from typing import Optional, Dict, Any


def collapse_background_bash_notifications(
    messages: list,
) -> list:
    """Collapse multiple background bash notifications into one.

    Args:
        messages: List of messages

    Returns:
        Collapsed messages
    """
    # Placeholder implementation
    return messages


def collapse_hook_summaries(hooks_output: list) -> list:
    """Collapse multiple hook outputs into a summary.

    Args:
        hooks_output: List of hook outputs

    Returns:
        Summarized hooks
    """
    return hooks_output


def collapse_read_search_results(
    results: list,
    max_results: int = 10,
) -> list:
    """Collapse read search results if too many.

    Args:
        results: Search results
        max_results: Maximum results to show

    Returns:
        Collapsed or original results
    """
    if len(results) > max_results:
        return results[:max_results] + [{"_collapsed": len(results) - max_results}]
    return results


def collapse_teammate_shutdowns(teammates: list) -> list:
    """Collapse teammate shutdown messages.

    Args:
        teammates: List of teammates

    Returns:
        Collapsed shutdown messages
    """
    return teammates


__all__ = [
    "collapse_background_bash_notifications",
    "collapse_hook_summaries",
    "collapse_read_search_results",
    "collapse_teammate_shutdowns",
]