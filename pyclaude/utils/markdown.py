"""
Markdown utilities.

Markdown parsing and rendering.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MarkdownElement:
    """Markdown element."""
    type: str
    content: str
    attributes: Dict[str, Any] = None


def parse_markdown(text: str) -> List[MarkdownElement]:
    """Parse markdown into elements.

    Args:
        text: Markdown text

    Returns:
        List of elements
    """
    elements = []
    lines = text.split("\n")

    for line in lines:
        if line.startswith("# "):
            elements.append(MarkdownElement(type="h1", content=line[2:]))
        elif line.startswith("## "):
            elements.append(MarkdownElement(type="h2", content=line[3:]))
        elif line.startswith("### "):
            elements.append(MarkdownElement(type="h3", content=line[4:]))
        elif line.startswith("- "):
            elements.append(MarkdownElement(type="list_item", content=line[2:]))
        elif line.strip() == "":
            elements.append(MarkdownElement(type="paragraph", content=""))
        else:
            elements.append(MarkdownElement(type="paragraph", content=line))

    return elements


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown.

    Args:
        text: Markdown text

    Returns:
        List of code blocks with language
    """
    pattern = r"```(\w*)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [{"language": lang, "code": code.strip()} for lang, code in matches]


def extract_links(text: str) -> List[Dict[str, str]]:
    """Extract links from markdown.

    Args:
        text: Markdown text

    Returns:
        List of links with text and URL
    """
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(pattern, text)
    return [{"text": text, "url": url} for text, url in matches]


def render_to_plain_text(markdown: str) -> str:
    """Convert markdown to plain text.

    Args:
        markdown: Markdown text

    Returns:
        Plain text
    """
    # Remove code blocks
    text = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    # Remove links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove emphasis
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    # Remove headers markers
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


__all__ = [
    "MarkdownElement",
    "parse_markdown",
    "extract_code_blocks",
    "extract_links",
    "render_to_plain_text",
]