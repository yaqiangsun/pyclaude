"""
Ink styles - Style definitions for terminal rendering.
"""
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re


class TextWrap(Enum):
    """Text wrapping mode."""
    WRAP = "wrap"
    TRUNCATE = "truncate"
    TRUNCATE_START = "truncate-start"
    TRUNCATE_MIDDLE = "truncate-middle"
    TRUNCATE_END = "truncate-end"


class Display(Enum):
    """Display mode."""
    FLEX = "flex"
    INLINE_FLEX = "inline-flex"
    NONE = "none"


class FlexDirection(Enum):
    """Flex direction."""
    ROW = "row"
    ROW_REVERSE = "row-reverse"
    COLUMN = "column"
    COLUMN_REVERSE = "column-reverse"


class JustifyContent(Enum):
    """Justify content."""
    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"


class AlignItems(Enum):
    """Align items."""
    FLEX_START = "flex-start"
    CENTER = "center"
    FLEX_END = "flex-end"
    STRETCH = "stretch"


# Color parsing
ANSI_COLORS = {
    'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
    'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
    'bright_black': 90, 'bright_red': 91, 'bright_green': 92,
    'bright_yellow': 93, 'bright_blue': 94, 'bright_magenta': 95,
    'bright_cyan': 96, 'bright_white': 97,
}

RGB_COLOR_RE = re.compile(r'#([0-9a-fA-F]{6})')
ANSI_256_RE = re.compile(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)')


@dataclass
class Color:
    """Color value."""
    type: str  # 'hex', 'ansi', 'rgb'
    value: Union[str, int, tuple]

    @classmethod
    def parse(cls, color_str: str) -> 'Color':
        """Parse a color string."""
        # Hex color
        if color_str.startswith('#'):
            match = RGB_COLOR_RE.match(color_str)
            if match:
                return cls(type='hex', value=color_str)

        # ANSI color name
        if color_str.lower() in ANSI_COLORS:
            return cls(type='ansi', value=ANSI_COLORS[color_str.lower()])

        # RGB
        match = ANSI_256_RE.match(color_str)
        if match:
            return cls(type='rgb', value=tuple(map(int, match.groups())))

        # Try as ANSI number
        try:
            return cls(type='ansi', value=int(color_str))
        except ValueError:
            pass

        return cls(type='ansi', value=37)  # Default white


@dataclass
class Styles:
    """Complete style object for a node."""
    # Display
    display: Display = Display.FLEX
    visibility: str = "visible"

    # Flexbox
    flex_direction: FlexDirection = FlexDirection.ROW
    justify_content: JustifyContent = JustifyContent.FLEX_START
    align_items: AlignItems = AlignItems.FLEX_START
    flex_gap: int = 0
    flex_wrap: bool = True

    # Sizing
    width: Optional[int] = None
    height: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None

    # Spacing
    margin_top: int = 0
    margin_right: int = 0
    margin_bottom: int = 0
    margin_left: int = 0
    padding_top: int = 0
    padding_right: int = 0
    padding_bottom: int = 0
    padding_left: int = 0

    # Border
    border_top: int = 0
    border_right: int = 0
    border_bottom: int = 0
    border_left: int = 0
    border_color: Optional[Color] = None
    border_style: str = "single"

    # Text
    text_wrap: TextWrap = TextWrap.WRAP
    text_color: Optional[Color] = None
    background_color: Optional[Color] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    inverse: bool = False
    dim: bool = False

    # Custom
    custom: Dict[str, Any] = field(default_factory=dict)


def merge_styles(*styles: Styles) -> Styles:
    """Merge multiple styles (later ones override earlier)."""
    result = Styles()
    for style in styles:
        for field_name in result.__dataclass_fields__:
            value = getattr(style, field_name)
            if value is not None and value != getattr(Styles(), field_name):
                setattr(result, field_name, value)
    return result


def styles_to_dict(styles: Styles) -> Dict[str, Any]:
    """Convert styles to dictionary."""
    result = {}
    for field_name in styles.__dataclass_fields__:
        value = getattr(styles, field_name)
        if isinstance(value, Enum):
            value = value.value
        if value is not None:
            result[field_name] = value
    return result


__all__ = [
    'TextWrap',
    'Display',
    'FlexDirection',
    'JustifyContent',
    'AlignItems',
    'Color',
    'Styles',
    'merge_styles',
    'styles_to_dict',
    'ANSI_COLORS',
]