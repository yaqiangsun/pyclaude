# Web Fetch Tool UI
# Reference: src/tools/WebFetchTool/UI.tsx (simplified)

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class WebFetchOutput:
    """Output from web fetch operation"""
    content: str
    url: str
    title: Optional[str] = None


def render_tool_use_message(url: str, prompt: str = None) -> str:
    """Render the tool use message"""
    parts = [f"Fetch: {url}"]
    if prompt:
        parts.append(f"({prompt[:50]}...)")
    return " ".join(parts)


def render_tool_result_message(output: WebFetchOutput, verbose: bool = False) -> str:
    """Render the tool result message"""
    lines = []

    if output.title:
        lines.append(f"=== {output.title} ===")
    lines.append(output.url)
    lines.append("")
    lines.append(output.content[:500] + "..." if len(output.content) > 500 else output.content)

    return '\n'.join(lines)