"""
Text highlighting utilities.

Syntax highlighting for terminal output.
"""

from typing import Dict, List, Optional, Tuple
import re


# Basic ANSI colors
COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "default": 39,
}


def colorize(text: str, color: str, bright: bool = False) -> str:
    """Colorize text with ANSI color.

    Args:
        text: Text to colorize
        color: Color name
        bright: Use bright variant

    Returns:
        Colorized text
    """
    code = COLORS.get(color.lower(), COLORS["default"])
    if bright:
        code += 60
    return f"\x1b[{code}m{text}\x1b[0m"


def highlight_syntax(code: str, language: str = "text") -> str:
    """Highlight code syntax.

    Args:
        code: Code to highlight
        language: Language type

    Returns:
        Highlighted code
    """
    # Simple placeholder - real implementation would use a syntax highlighter
    return code


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """Highlight keywords in text.

    Args:
        text: Text to highlight
        keywords: Keywords to highlight

    Returns:
        Text with highlighted keywords
    """
    result = text
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        result = pattern.sub(colorize(kw, "green"), result)
    return result


__all__ = [
    "COLORS",
    "colorize",
    "highlight_syntax",
    "highlight_keywords",
]