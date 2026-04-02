"""
CLI highlight utilities.

Provides syntax highlighting for CLI output.
"""

import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

# Shared promise for cli-highlight
_cli_highlight_promise = None


@dataclass
class CliHighlight:
    """CLI highlight interface."""
    highlight: Optional[callable] = None
    supports_language: Optional[callable] = None


# Language name mapping (simplified)
_LANGUAGE_MAP = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "jsx": "JavaScript",
    "tsx": "TypeScript",
    "py": "Python",
    "rb": "Ruby",
    "go": "Go",
    "rs": "Rust",
    "java": "Java",
    "c": "C",
    "cpp": "C++",
    "h": "C/C++ Header",
    "hpp": "C++ Header",
    "cs": "C#",
    "php": "PHP",
    "swift": "Swift",
    "kt": "Kotlin",
    "scala": "Scala",
    "sh": "Shell",
    "bash": "Bash",
    "zsh": "Zsh",
    "fish": "Fish",
    "json": "JSON",
    "yaml": "YAML",
    "yml": "YAML",
    "toml": "TOML",
    "xml": "XML",
    "html": "HTML",
    "css": "CSS",
    "scss": "SCSS",
    "sql": "SQL",
    "md": "Markdown",
    "markdown": "Markdown",
    "dockerfile": "Dockerfile",
    "r": "R",
    "lua": "Lua",
    "pl": "Perl",
    "ex": "Elixir",
    "exs": "Elixir",
    "erl": "Erlang",
    "hs": "Haskell",
    "elm": "Elm",
    "clj": "Clojure",
    "vim": "Vim",
    "makefile": "Makefile",
}


async def _load_cli_highlight() -> Optional[CliHighlight]:
    """Load cli-highlight module."""
    try:
        # Try to import cli-highlight
        # In practice this would use the actual library
        return CliHighlight(
            highlight=lambda code, **kwargs: code,
            supports_language=lambda lang: lang in _LANGUAGE_MAP,
        )
    except Exception:
        return None


def get_cli_highlight_promise() -> Optional[CliHighlight]:
    """Get the shared cli-highlight promise."""
    global _cli_highlight_promise
    if _cli_highlight_promise is None:
        _cli_highlight_promise = _load_cli_highlight()
    return _cli_highlight_promise


async def get_language_name(file_path: str) -> str:
    """Get language name from file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language name or "unknown"
    """
    ext = Path(file_path).suffix.lstrip(".")
    if not ext:
        return "unknown"
    return _LANGUAGE_MAP.get(ext.lower(), "unknown")


__all__ = [
    "CliHighlight",
    "get_cli_highlight_promise",
    "get_language_name",
]