"""
Ink components - Terminal UI components adapted for Python.

Box: Like a div with flexbox layout
Text: Styled text with colors and formatting
"""
from typing import Optional, List, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console, ConsoleOptions, RenderableType
from rich.text import Text as RichText
from rich.panel import Panel
from rich.box import Box as RichBox
from rich.style import Style


class TextAlign(Enum):
    """Text alignment."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TextWrap(Enum):
    """Text wrapping mode."""
    WRAP = "wrap"
    TRUNCATE = "truncate"
    TRUNCATE_START = "truncate-start"
    TRUNCATE_MIDDLE = "truncate-middle"
    TRUNCATE_END = "truncate-end"


@dataclass
class BoxStyles:
    """Styles for Box component."""
    # Layout
    display: str = "flex"
    flex_direction: str = "row"
    justify_content: str = "flex-start"
    align_items: str = "flex-start"
    flex_gap: int = 0
    margin: int = 0
    padding: int = 0
    # Sizing
    width: Optional[int] = None
    height: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    # Border
    border_style: str = ""
    border_color: Optional[str] = None
    # Visibility
    visibility: str = "visible"


@dataclass
class TextStyles:
    """Styles for Text component."""
    # Colors
    color: Optional[str] = None
    background_color: Optional[str] = None
    # Formatting
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    inverse: bool = False
    bold: bool = False
    dim: bool = False
    # Alignment
    text_align: TextAlign = TextAlign.LEFT
    # Wrapping
    wrap: TextWrap = TextWrap.WRAP


class Box:
    """
    Box is an essential component to build layouts.
    Like <div style="display: flex"> in the browser.
    """

    def __init__(
        self,
        children: Optional[List[RenderableType]] = None,
        **styles: Any,
    ):
        self.children = children or []
        self.styles = BoxStyles(**{k.replace('-', '_'): v for k, v in styles.items()})

    def set_children(self, children: List[RenderableType]) -> None:
        """Set children for this box."""
        self.children = children

    def render(self, console: Optional[Console] = None) -> RenderableType:
        """Render the box and its children."""
        if not self.children:
            return ""

        # Simple rendering - join children
        content = ""
        for child in self.children:
            if hasattr(child, 'render'):
                content += str(child.render(console))
            else:
                content += str(child)

        if self.styles.border_style:
            border_style = Style.parse(self.styles.border_color) if self.styles.border_color else None
            return Panel(content, border_style=border_style or self.styles.border_style)

        return content


class Text:
    """
    Text component for displaying styled text.
    """

    def __init__(
        self,
        content: str = "",
        **styles: Any,
    ):
        self.content = content
        # Convert kebab-case to snake_case for styles
        normalized_styles = {k.replace('-', '_'): v for k, v in styles.items()}
        self.styles = TextStyles(**normalized_styles)

    def render(self, console: Optional[Console] = None) -> RichText:
        """Render the text with styles."""
        style = Style(
            color=self.styles.color,
            bgcolor=self.styles.background_color,
            italic=self.styles.italic,
            underline=self.styles.underline,
            strikethrough=self.styles.strikethrough,
            inverse=self.styles.inverse,
            bold=self.styles.bold,
            dim=self.styles.dim,
        )
        return RichText(self.content, style=style)

    def __str__(self) -> str:
        """String representation."""
        return self.content


class Spacer:
    """A spacer component that fills remaining space."""

    def __init__(self, length: int = 1):
        self.length = length

    def render(self, console: Optional[Console] = None) -> str:
        return " " * self.length

    def __str__(self) -> str:
        return " " * self.length


class Newline:
    """A newline character."""

    def __init__(self, count: int = 1):
        self.count = count

    def render(self, console: Optional[Console] = None) -> str:
        return "\n" * self.count

    def __str__(self) -> str:
        return "\n" * self.count


class Link:
    """A clickable link component."""

    def __init__(self, url: str, children: Optional[RenderableType] = None):
        self.url = url
        self.children = children

    def render(self, console: Optional[Console] = None) -> str:
        child_content = ""
        if self.children:
            if hasattr(self.children, 'render'):
                child_content = str(self.children.render(console))
            else:
                child_content = str(self.children)

        # Render as ANSI link
        return f"\x1b]8;;{self.url}\x1b\\{child_content}\x1b]8;;\x1b\\"

    def __str__(self) -> str:
        return self.render()


class Button:
    """A button component."""

    def __init__(
        self,
        children: Optional[RenderableType] = None,
        variant: str = "default",
        isFocused: bool = False,
        on_click: Optional[Callable] = None,
    ):
        self.children = children
        self.variant = variant
        self.is_focused = isFocused
        self.on_click = on_click

    def render(self, console: Optional[Console] = None) -> str:
        child_content = ""
        if self.children:
            if hasattr(self.children, 'render'):
                child_content = str(self.children.render(console))
            else:
                child_content = str(self.children)

        # Simple button rendering
        if self.is_focused:
            return f"[{self.variant}]{child_content}[/{self.variant}]"
        return child_content

    def __str__(self) -> str:
        return self.render()


class NoSelect:
    """Component that prevents text selection."""

    def __init__(self, children: Optional[RenderableType] = None):
        self.children = children

    def render(self, console: Optional[Console] = None) -> RenderableType:
        if self.children:
            if hasattr(self.children, 'render'):
                return self.children.render(console)
            return self.children
        return ""


class ScrollBox:
    """A scrollable box component."""

    def __init__(
        self,
        children: Optional[List[RenderableType]] = None,
        overflow_x: bool = False,
        overflow_y: bool = True,
    ):
        self.children = children or []
        self.overflow_x = overflow_x
        self.overflow_y = overflow_y

    def render(self, console: Optional[Console] = None) -> str:
        content = ""
        for child in self.children:
            if hasattr(child, 'render'):
                content += str(child.render(console))
            else:
                content += str(child)
        return content


# Export all components
__all__ = [
    'Box',
    'BoxStyles',
    'Text',
    'TextStyles',
    'TextAlign',
    'TextWrap',
    'Spacer',
    'Newline',
    'Link',
    'Button',
    'NoSelect',
    'ScrollBox',
]