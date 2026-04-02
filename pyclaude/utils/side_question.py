"""
Side question utilities.

Side question handling.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class SideQuestionType(str, Enum):
    """Side question types."""
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    SELECTION = "selection"


@dataclass
class SideQuestion:
    """A side question."""
    id: str
    type: SideQuestionType
    question: str
    options: Optional[List[str]] = None
    answer: Optional[str] = None


def create_confirmation(
    question: str,
) -> SideQuestion:
    """Create confirmation question.

    Args:
        question: Question text

    Returns:
        Side question
    """
    import uuid
    return SideQuestion(
        id=str(uuid.uuid4()),
        type=SideQuestionType.CONFIRMATION,
        question=question,
    )


def create_selection(
    question: str,
    options: List[str],
) -> SideQuestion:
    """Create selection question.

    Args:
        question: Question text
        options: Selection options

    Returns:
        Side question
    """
    import uuid
    return SideQuestion(
        id=str(uuid.uuid4()),
        type=SideQuestionType.SELECTION,
        question=question,
        options=options,
    )


__all__ = [
    "SideQuestionType",
    "SideQuestion",
    "create_confirmation",
    "create_selection",
]