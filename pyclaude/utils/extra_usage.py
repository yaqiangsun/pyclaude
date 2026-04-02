"""
Extra usage billing utilities.

Check if usage is billed as extra based on model and mode.
"""

import re
from typing import Optional

# Stub - will be imported from auth when available
def is_claude_ai_subscriber() -> bool:
    """Check if user is a Claude AI subscriber."""
    return False


# Stub - will be imported from context when available
def has_1m_context(model: str) -> bool:
    """Check if model has 1M context."""
    return bool(re.search(r"\[1m\]", model, re.IGNORECASE))


def is_billed_as_extra_usage(
    model: Optional[str],
    is_fast_mode: bool,
    is_opus_1m_merged: bool,
) -> bool:
    """Check if usage should be billed as extra.

    Args:
        model: The model name
        is_fast_mode: Whether in fast mode
        is_opus_1m_merged: Whether Opus 1M is merged

    Returns:
        True if billed as extra usage
    """
    if not is_claude_ai_subscriber():
        return False
    if is_fast_mode:
        return True
    if model is None or not has_1m_context(model):
        return False

    m = model.lower().replace("[1m]", "").strip()
    is_opus_46 = m == "opus" or "opus-4-6" in m
    is_sonnet_46 = m == "sonnet" or "sonnet-4-6" in m

    if is_opus_46 and is_opus_1m_merged:
        return False

    return is_opus_46 or is_sonnet_46


__all__ = ["is_billed_as_extra_usage"]