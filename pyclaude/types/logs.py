"""Types for logs."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LogType(str, Enum):
    """Log entry types."""
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'
    TOOL_USE = 'tool_use'
    TOOL_RESULT = 'tool_result'
    PROGRESS = 'progress'
    CONTENT_REPLACEMENT = 'content-replacement'


@dataclass
class SerializedMessage:
    """A serialized message."""
    type: str
    role: str
    content: str
    timestamp: float = 0
    uuid: str = ''
    session_id: str = ''
    is_sidechain: bool = False


@dataclass
class TranscriptMessage:
    """A message in the transcript."""
    type: str
    role: str
    content: Any
    uuid: str
    session_id: str
    timestamp: float = 0
    parent_uuid: Optional[str] = None
    forked_from: Optional[Dict[str, str]] = None
    is_sidechain: bool = False


@dataclass
class ContentReplacementEntry:
    """Entry for content replacement."""
    type: str = 'content-replacement'
    session_id: str = ''
    replacements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LogOption:
    """Options for logging."""
    date: str = ''
    messages: List[SerializedMessage] = field(default_factory=list)
    full_path: str = ''
    value: int = 0
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    first_prompt: str = ''
    message_count: int = 0
    is_sidechain: bool = False
    session_id: str = ''
    custom_title: Optional[str] = None
    content_replacements: List[Dict[str, Any]] = field(default_factory=list)


__all__ = [
    'LogType',
    'SerializedMessage',
    'TranscriptMessage',
    'ContentReplacementEntry',
    'LogOption',
]