"""Memory scan utilities."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pyclaude.utils.frontmatter_parser import parse_frontmatter

# Memory types
MEMORY_TYPES = ['user', 'feedback', 'project', 'reference']

# Constants
MAX_MEMORY_FILES = 200
FRONTMATTER_MAX_LINES = 30


@dataclass
class MemoryHeader:
    """Memory file header information."""
    filename: str
    file_path: str
    mtime_ms: float
    description: Optional[str]
    type: Optional[str]


def parse_memory_type(raw) -> Optional[str]:
    """Parse a raw frontmatter value into a MemoryType.

    Invalid or missing values return None — legacy files without a
    type: field keep working, files with unknown types degrade gracefully.
    """
    if not isinstance(raw, str):
        return None
    if raw in MEMORY_TYPES:
        return raw
    return None


def read_file_in_range(file_path: str, start: int, end: int = None):
    """Read a range of lines from a file.

    Returns (content, mtime_ms).
    """
    path = Path(file_path)
    if not path.exists():
        return '', 0

    try:
        stat = path.stat()
        mtime_ms = stat.st_mtime
    except OSError:
        mtime_ms = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if end is None:
                end = len(lines)
            content = ''.join(lines[start:end])
            return content, mtime_ms
    except (OSError, IOError):
        return '', mtime_ms


async def scan_memory_files(memory_dir: str, signal=None) -> list[MemoryHeader]:
    """Scan a memory directory for .md files, read their frontmatter, and return
    a header list sorted newest-first (capped at MAX_MEMORY_FILES).

    Args:
        memory_dir: Path to memory directory
        signal: Optional abort signal (ignored in Python, for compatibility)

    Returns:
        List of MemoryHeader sorted by mtime (newest first)
    """
    memories = []
    memory_path = Path(memory_dir)

    if not memory_path.exists():
        return memories

    if not memory_path.is_dir():
        return memories

    try:
        # Recursively find all .md files
        md_files = []
        for root, dirs, files in os.walk(memory_dir):
            for f in files:
                if f.endswith('.md') and f != 'MEMORY.md':
                    rel_path = os.path.relpath(os.path.join(root, f), memory_dir)
                    md_files.append(rel_path)
    except PermissionError:
        return memories

    # Process each file
    for relative_path in md_files:
        file_path = os.path.join(memory_dir, relative_path)

        try:
            # Read only frontmatter lines for efficiency
            content, mtime_ms = read_file_in_range(file_path, 0, FRONTMATTER_MAX_LINES)
            frontmatter, _ = parse_frontmatter(content)

            description = None
            if frontmatter and 'description' in frontmatter:
                description = frontmatter['description']

            memory_type = None
            if frontmatter and 'type' in frontmatter:
                memory_type = parse_memory_type(frontmatter['type'])

            header = MemoryHeader(
                filename=relative_path,
                file_path=file_path,
                mtime_ms=mtime_ms,
                description=description,
                type=memory_type,
            )
            memories.append(header)

        except Exception:
            continue

    # Sort by mtime (newest first), cap at MAX_MEMORY_FILES
    memories.sort(key=lambda m: m.mtime_ms, reverse=True)
    return memories[:MAX_MEMORY_FILES]


def format_memory_manifest(memories: list[MemoryHeader]) -> str:
    """Format memory headers as a text manifest.

    One line per file with [type] filename (timestamp): description.
    """
    lines = []
    for m in memories:
        tag = f'[{m.type}] ' if m.type else ''
        ts = ''
        if m.mtime_ms > 0:
            ts = f' ({int(m.mtime_ms)})'

        if m.description:
            line = f'- {tag}{m.filename}{ts}: {m.description}'
        else:
            line = f'- {tag}{m.filename}{ts}'

        lines.append(line)

    return '\n'.join(lines)


def scan_memories(memory_dir: str) -> list[dict]:
    """Scan memory directory for memory files.

    Returns a list of memory dictionaries (legacy format).
    """
    import asyncio

    # Run async version synchronously
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    memories = loop.run_until_complete(scan_memory_files(memory_dir))

    # Convert to dict format
    return [
        {
            'filename': m.filename,
            'file_path': m.file_path,
            'mtime_ms': m.mtime_ms,
            'description': m.description,
            'type': m.type,
        }
        for m in memories
    ]


def find_relevant_memories(memory_dir: str, query: str) -> list[dict]:
    """Find memories relevant to a query.

    Simple relevance matching based on filename and description.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    memories = loop.run_until_complete(scan_memory_files(memory_dir))

    if not query:
        return [
            {
                'filename': m.filename,
                'file_path': m.file_path,
                'description': m.description,
                'type': m.type,
            }
            for m in memories[:10]
        ]

    query_lower = query.lower()
    relevant = []

    for m in memories:
        # Score based on matches
        score = 0

        # Exact match in description
        if m.description and query_lower in m.description.lower():
            score += 10

        # Exact match in filename
        if query_lower in m.filename.lower():
            score += 5

        if score > 0:
            relevant.append({
                'filename': m.filename,
                'file_path': m.file_path,
                'description': m.description,
                'type': m.type,
                'score': score,
            })

    # Sort by score
    relevant.sort(key=lambda x: x.get('score', 0), reverse=True)
    return relevant[:10]


__all__ = [
    'MemoryHeader',
    'MEMORY_TYPES',
    'MAX_MEMORY_FILES',
    'parse_memory_type',
    'scan_memory_files',
    'format_memory_manifest',
    'scan_memories',
    'find_relevant_memories',
]