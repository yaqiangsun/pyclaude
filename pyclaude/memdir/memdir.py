"""Memory directory module."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Optional

ENTRYPOINT_NAME = 'MEMORY.md'
MAX_ENTRYPOINT_LINES = 200
MAX_ENTRYPOINT_BYTES = 25_000


class EntrypointTruncation:
    """Truncation result for MEMORY.md."""

    def __init__(
        self,
        content: str,
        line_count: int,
        byte_count: int,
        was_line_truncated: bool,
        was_byte_truncated: bool,
    ):
        self.content = content
        self.line_count = line_count
        self.byte_count = byte_count
        self.was_line_truncated = was_line_truncated
        self.was_byte_truncated = was_byte_truncated


def truncate_entrypoint_content(raw: str) -> EntrypointTruncation:
    """Truncate MEMORY.md content to line and byte caps."""
    trimmed = raw.strip()
    content_lines = trimmed.split('\n')
    line_count = len(content_lines)
    byte_count = len(trimmed)

    was_line_truncated = line_count > MAX_ENTRYPOINT_LINES
    was_byte_truncated = byte_count > MAX_ENTRYPOINT_BYTES

    if not was_line_truncated and not was_byte_truncated:
        return EntrypointTruncation(
            trimmed, line_count, byte_count, was_line_truncated, was_byte_truncated
        )

    truncated = (
        content_lines[:MAX_ENTRYPOINT_LINES]
        if was_line_truncated
        else trimmed
    )

    if len(truncated) > MAX_ENTRYPOINT_BYTES:
        cut_at = truncated.rfind('\n', 0, MAX_ENTRYPOINT_BYTES)
        truncated = truncated[: cut_at if cut_at > 0 else MAX_ENTRYPOINT_BYTES]

    reason = ''
    if was_byte_truncated and not was_line_truncated:
        reason = f'{byte_count} bytes (limit: {MAX_ENTRYPOINT_BYTES})'
    elif was_line_truncated and not was_byte_truncated:
        reason = f'{line_count} lines (limit: {MAX_ENTRYPOINT_LINES})'
    else:
        reason = f'{line_count} lines and {byte_count} bytes'

    truncated += f'\n\n> WARNING: {ENTRYPOINT_NAME} is {reason}. Only part was loaded.'

    return EntrypointTruncation(
        truncated, line_count, byte_count, was_line_truncated, was_byte_truncated
    )


def get_memdir_path() -> str:
    """Get the memory directory path."""
    # TODO: implement with actual config
    home = os.path.expanduser('~')
    return os.path.join(home, '.claude', 'projects', 'memory')


def is_memdir_enabled() -> bool:
    """Check if memory directory is enabled."""
    # TODO: implement with actual settings
    return True


async def ensure_memory_dir_exists(memory_dir: str) -> None:
    """Ensure a memory directory exists."""
    os.makedirs(memory_dir, exist_ok=True)


def build_memory_lines(
    display_name: str,
    memory_dir: str,
    extra_guidelines: Optional[list[str]] = None,
    skip_index: bool = False,
) -> list[str]:
    """Build the typed-memory behavioral instructions."""
    # Simplified version
    lines = [
        f'# {display_name}',
        '',
        f'You have a persistent memory system at `{memory_dir}`.',
        '',
        'When the user explicitly asks you to remember something, save it immediately.',
        '',
    ]

    if extra_guidelines:
        lines.extend(extra_guidelines)

    return lines


def build_memory_prompt(
    display_name: str,
    memory_dir: str,
    extra_guidelines: Optional[list[str]] = None,
) -> str:
    """Build the typed-memory prompt with MEMORY.md content."""
    entrypoint_path = os.path.join(memory_dir, ENTRYPOINT_NAME)

    # Read existing memory entrypoint
    entrypoint_content = ''
    if os.path.exists(entrypoint_path):
        with open(entrypoint_path, 'r') as f:
            entrypoint_content = f.read()

    lines = build_memory_lines(display_name, memory_dir, extra_guidelines)

    if entrypoint_content.strip():
        t = truncate_entrypoint_content(entrypoint_content)
        lines.extend(['', f'## {ENTRYPOINT_NAME}', '', t.content])
    else:
        lines.extend([
            '',
            f'## {ENTRYPOINT_NAME}',
            '',
            f'Your {ENTRYPOINT_NAME} is currently empty.',
        ])

    return '\n'.join(lines)


async def load_memory_prompt() -> Optional[str]:
    """Load the unified memory prompt."""
    if not is_memdir_enabled():
        return None

    memory_dir = get_memdir_path()
    await ensure_memory_dir_exists(memory_dir)
    return build_memory_prompt('auto memory', memory_dir)


__all__ = [
    'ENTRYPOINT_NAME',
    'MAX_ENTRYPOINT_LINES',
    'MAX_ENTRYPOINT_BYTES',
    'EntrypointTruncation',
    'truncate_entrypoint_content',
    'get_memdir_path',
    'is_memdir_enabled',
    'ensure_memory_dir_exists',
    'build_memory_lines',
    'build_memory_prompt',
    'load_memory_prompt',
]