"""
Prompt category utilities.

Categorize prompts for handling.
"""

from typing import Optional
from enum import Enum


class PromptCategory(str, Enum):
    """Prompt categories."""
    GENERAL = "general"
    CODE = "code"
    DEBUG = "debug"
    REFACTOR = "refactor"
    TEST = "test"
    DOCUMENT = "document"


def categorize_prompt(text: str) -> PromptCategory:
    """Categorize a prompt.

    Args:
        text: Prompt text

    Returns:
        Prompt category
    """
    text_lower = text.lower()

    if any(kw in text_lower for kw in ["debug", "error", "fix", "bug"]):
        return PromptCategory.DEBUG
    if any(kw in text_lower for kw in ["refactor", "improve", "clean"]):
        return PromptCategory.REFACTOR
    if any(kw in text_lower for kw in ["test", "spec"]):
        return PromptCategory.TEST
    if any(kw in text_lower for kw in ["doc", "document", "comment"]):
        return PromptCategory.DOCUMENT
    if any(kw in text_lower for kw in ["code", "write", "implement", "function"]):
        return PromptCategory.CODE

    return PromptCategory.GENERAL


__all__ = [
    "PromptCategory",
    "categorize_prompt",
]