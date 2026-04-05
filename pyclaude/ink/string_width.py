"""String width calculation for terminal rendering."""
import re
from typing import Optional

try:
    import wcwidth
    _HAS_WCWIDTH = True
except ImportError:
    _HAS_WCWIDTH = False


# Emoji regex pattern
EMOJI_REGEX = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # Emoji symbols
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport/map symbols
    "\U0001F1E0-\U0001F1FF"  # Flag emojis
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed characters
    "]+"
)


def _is_pure_ascii(s: str) -> bool:
    """Check if string is pure ASCII."""
    for char in s:
        code = ord(char)
        if code >= 127 or code == 0x1b:  # ANSI escape
            return False
    return True


def _count_printable(s: str) -> int:
    """Count printable ASCII characters."""
    width = 0
    for char in s:
        code = ord(char)
        if code > 0x1f:  # Exclude control chars
            width += 1
    return width


def _strip_ansi(s: str) -> str:
    """Strip ANSI escape codes."""
    # Simple ANSI strip - remove escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)


def _needs_segmentation(s: str) -> bool:
    """Check if string needs grapheme segmentation."""
    for char in s:
        cp = ord(char)
        # Emoji ranges
        if 0x1f300 <= cp <= 0x1faff:
            return True
        if 0x2600 <= cp <= 0x27bf:
            return True
        if 0x1f1e6 <= cp <= 0x1f1ff:
            return True
        # Variation selectors, ZWJ
        if 0xfe00 <= cp <= 0xfe0f:
            return True
        if ord('\u200d') == cp:
            return True
    return False


def _is_zero_width(cp: int) -> bool:
    """Check if codepoint is zero-width."""
    # Fast path for common printable range
    if 0x20 <= cp < 0x7f:
        return False
    if 0xa0 <= cp < 0x0300:
        return cp == 0x00ad

    # Control characters
    if cp <= 0x1f or (0x7f <= cp <= 0x9f):
        return True

    # Zero-width characters
    if 0x200b <= cp <= 0x200d:  # ZW space/joiner
        return True
    if cp == 0xfeff:  # BOM
        return True
    if 0x2060 <= cp <= 0x2064:  # Word joiner etc.
        return True

    # Variation selectors
    if 0xfe00 <= cp <= 0xfe0f or 0xe0100 <= cp <= 0xe01ef:
        return True

    # Combining diacritical marks
    if (0x0300 <= cp <= 0x036f or
        0x1dc0 <= cp <= 0x1dff or
        0x20d0 <= cp <= 0x20ff or
        0xfe20 <= cp <= 0xfe2f):
        return True

    return False


def string_width(s: str) -> int:
    """Get the display width of a string as it would appear in a terminal.

    This correctly handles:
    - ASCII characters
    - Wide characters (CJK)
    - Emoji
    - Combining characters
    - ANSI escape codes
    """
    if not isinstance(s, str) or len(s) == 0:
        return 0

    # Fast path: pure ASCII
    if _is_pure_ascii(s):
        return _count_printable(s)

    # Strip ANSI codes if present
    if '\x1b' in s:
        s = _strip_ansi(s)
        if len(s) == 0:
            return 0

    # Use wcwidth if available
    if _HAS_WCWIDTH:
        width = 0
        for char in s:
            w = wcwidth.wcwidth(char)
            if w is None:
                w = 0
            width += w
        return width

    # Fallback: basic width calculation
    width = 0
    for char in s:
        cp = ord(char)
        if not _is_zero_width(cp):
            # Check if it's a wide character
            if (0x1100 <= cp <= 0x115f or
                0x2329 <= cp <= 0x232a or
                0x2e80 <= cp <= 0x303e or
                0x3040 <= cp <= 0xa4cf or
                0xac00 <= cp <= 0xd7a3 or
                0xf900 <= cp <= 0xfaff or
                0xfe10 <= cp <= 0xfe19 or
                0xfe30 <= cp <= 0xfe6f or
                0xff00 <= cp <= 0xff60 or
                0xffe0 <= cp <= 0xffe6 or
                0x20000 <= cp <= 0x2fffd or
                0x30000 <= cp <= 0x3fffd):
                width += 2
            else:
                width += 1
    return width


__all__ = ['string_width']