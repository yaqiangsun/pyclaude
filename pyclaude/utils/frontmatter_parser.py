"""
Frontmatter parser utilities.

Parse YAML frontmatter from files.
"""

import re
from typing import Optional, Dict, Any


FRONTMATTER_REGEX = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL
)


def parse_frontmatter(content: str) -> tuple[Optional[Dict[str, Any]], str]:
    """Parse frontmatter from content.

    Args:
        content: File content

    Returns:
        (frontmatter_dict, remaining_content)
    """
    match = FRONTMATTER_REGEX.match(content)
    if not match:
        return None, content

    frontmatter_text = match.group(1)
    remaining = content[match.end():]

    # Simple key: value parser
    result = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip()

    return result, remaining


def add_frontmatter(content: str, frontmatter: Dict[str, Any]) -> str:
    """Add frontmatter to content.

    Args:
        content: File content
        frontmatter: Frontmatter dict

    Returns:
        Content with frontmatter
    """
    fm_lines = ["---"]
    for key, value in frontmatter.items():
        fm_lines.append(f"{key}: {value}")
    fm_lines.append("---")
    fm_lines.append("")

    return "\n".join(fm_lines) + content


__all__ = [
    "parse_frontmatter",
    "add_frontmatter",
    "FRONTMATTER_REGEX",
]