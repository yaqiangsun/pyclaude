"""
Ink ANSI - ANSI escape code handling.
"""
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass


# ANSI escape sequence regex
ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
CSI_SEQUENCE_RE = re.compile(r'\x1b\[([0-9;]*)([a-zA-Z])')
SGR_CODES = {
    'reset': 0,
    'bold': 1,
    'dim': 2,
    'italic': 3,
    'underline': 4,
    'blink': 5,
    'reverse': 7,
    'hidden': 8,
    'strikethrough': 9,
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'bright_black': 90,
    'bright_red': 91,
    'bright_green': 92,
    'bright_yellow': 93,
    'bright_blue': 94,
    'bright_magenta': 95,
    'bright_cyan': 96,
    'bright_white': 97,
}


@dataclass
class AnsiSegment:
    """A segment of ANSI-formatted text."""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    foreground: Optional[str] = None
    background: Optional[str] = None


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return ANSI_ESCAPE_RE.sub('', text)


def parse_ansi(text: str) -> List[AnsiSegment]:
    """
    Parse ANSI-formatted text into segments.

    Args:
        text: Text with ANSI codes

    Returns:
        List of text segments with styles
    """
    segments = []
    current_pos = 0
    current_style = {
        'bold': False,
        'italic': False,
        'underline': False,
        'strikethrough': False,
        'foreground': None,
        'background': None,
    }

    # Find all matches
    for match in ANSI_ESCAPE_RE.finditer(text):
        # Add text before this match
        if match.start() > current_pos:
            segments.append(AnsiSegment(
                text=text[current_pos:match.start()],
                **current_style,
            ))

        # Parse the escape sequence
        seq = match.group()
        params, final_char = _parse_csi(seq)

        if final_char == 'm':  # SGR (Select Graphic Rendition)
            _update_style(current_style, params)
        elif final_char == 'K':  # Erase in Line
            pass  # Handle if needed

        current_pos = match.end()

    # Add remaining text
    if current_pos < len(text):
        segments.append(AnsiSegment(
            text=text[current_pos:],
            **current_style,
        ))

    return segments


def _parse_csi(seq: str) -> Tuple[List[int], str]:
    """Parse a CSI sequence."""
    match = CSI_SEQUENCE_RE.match(seq)
    if not match:
        return [], ''

    params_str = match.group(1)
    final_char = match.group(2)

    if params_str:
        params = [int(p) for p in params_str.split(';') if p]
    else:
        params = []

    return params, final_char


def _update_style(style: dict, params: List[int]) -> None:
    """Update current style from SGR parameters."""
    i = 0
    while i < len(params):
        code = params[i]

        if code == 0:
            style.update({
                'bold': False,
                'italic': False,
                'underline': False,
                'strikethrough': False,
                'foreground': None,
                'background': None,
            })
        elif code == 1:
            style['bold'] = True
        elif code == 3:
            style['italic'] = True
        elif code == 4:
            style['underline'] = True
        elif code == 9:
            style['strikethrough'] = True
        elif code == 22:
            style['bold'] = False
        elif code == 23:
            style['italic'] = False
        elif code == 24:
            style['underline'] = False
        elif code == 29:
            style['strikethrough'] = False
        elif 30 <= code <= 37:
            style['foreground'] = _color_code_to_name(code - 30)
        elif code == 39:
            style['foreground'] = None
        elif 40 <= code <= 47:
            style['background'] = _color_code_to_name(code - 40)
        elif code == 49:
            style['background'] = None
        elif 90 <= code <= 97:
            style['foreground'] = _color_code_to_name(code - 90, bright=True)
        elif 100 <= code <= 107:
            style['background'] = _color_code_to_name(code - 100, bright=True)

        i += 1


def _color_code_to_name(code: int, bright: bool = False) -> str:
    """Convert color code to color name."""
    names = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    name = names[code] if code < len(names) else 'white'
    return f'bright_{name}' if bright else name


def to_ansi(text: str, **styles) -> str:
    """Convert styled text to ANSI codes."""
    codes = []

    if styles.get('bold'):
        codes.append('1')
    if styles.get('italic'):
        codes.append('3')
    if styles.get('underline'):
        codes.append('4')
    if styles.get('strikethrough'):
        codes.append('9')

    fg = styles.get('foreground')
    if fg and fg in SGR_CODES:
        codes.append(str(SGR_CODES[fg]))

    if codes:
        return f'\x1b[{";".join(codes)}m{text}\x1b[0m'
    return text


__all__ = [
    'AnsiSegment',
    'strip_ansi',
    'parse_ansi',
    'to_ansi',
    'SGR_CODES',
]