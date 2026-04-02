"""
Prompt editor utilities.

Edit prompts before sending.
"""

from typing import List, Dict, Any


def edit_prompt(prompt: str, edits: List[Dict[str, Any]]) -> str:
    """Edit prompt with changes.

    Args:
        prompt: Original prompt
        edits: List of edits

    Returns:
        Edited prompt
    """
    result = prompt
    for edit in edits:
        old = edit.get("old_string", "")
        new = edit.get("new_string", "")
        if edit.get("replace_all"):
            result = result.replace(old, new)
        else:
            result = result.replace(old, new, 1)
    return result


__all__ = ["edit_prompt"]