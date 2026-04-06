"""
Design system - Themed components for ink.
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.theme import Theme
from rich.style import Style


class ThemeMode(Enum):
    """Theme mode."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


# Default theme colors
DEFAULT_LIGHT_COLORS = {
    "black": "#000000",
    "red": "#e74856",
    "green": "#16c60c",
    "yellow": "#f9f1a5",
    "blue": "#3b96ff",
    "magenta": "#b4009e",
    "cyan": "#00d7aa",
    "white": "#ffffff",
    "bright_black": "#767676",
    "bright_red": "#ff6b6b",
    "bright_green": "#6bff6b",
    "bright_yellow": "#ffff6b",
    "bright_blue": "#6b6bff",
    "bright_magenta": "#ff6bff",
    "bright_cyan": "#6bffff",
    "bright_white": "#ffffff",
}

DEFAULT_DARK_COLORS = {
    "black": "#000000",
    "red": "#e74856",
    "green": "#16c60c",
    "yellow": "#f9f1a5",
    "blue": "#3b96ff",
    "magenta": "#b4009e",
    "cyan": "#00d7aa",
    "white": "#ffffff",
    "bright_black": "#767676",
    "bright_red": "#ff6b6b",
    "bright_green": "#6bff6b",
    "bright_yellow": "#ffff6b",
    "bright_blue": "#6b6bff",
    "bright_magenta": "#ff6bff",
    "bright_cyan": "#6bffff",
    "bright_white": "#ffffff",
}


@dataclass
class ThemeColors:
    """Theme color palette."""
    # Base colors
    black: str = "#000000"
    red: str = "#e74856"
    green: str = "#16c60c"
    yellow: str = "#f9f1a5"
    blue: str = "#3b96ff"
    magenta: str = "#b4009e"
    cyan: str = "#00d7aa"
    white: str = "#ffffff"

    # Bright colors
    bright_black: str = "#767676"
    bright_red: str = "#ff6b6b"
    bright_green: str = "#6bff6b"
    bright_yellow: str = "#ffff6b"
    bright_blue: str = "#6b6bff"
    bright_magenta: str = "#ff6bff"
    bright_cyan: str = "#6bffff"
    bright_white: str = "#ffffff"

    # Semantic colors
    success: str = "#16c60c"
    warning: str = "#f9f1a5"
    error: str = "#e74856"
    info: str = "#3b96ff"

    # UI colors
    background: str = "#ffffff"
    foreground: str = "#000000"
    accent: str = "#3b96ff"
    muted: str = "#767676"


@dataclass
class ThemeConfig:
    """Theme configuration."""
    mode: ThemeMode = ThemeMode.AUTO
    colors: ThemeColors = field(default_factory=ThemeColors)
    font_style: str = "normal"


class ThemeProvider:
    """Theme provider context."""

    _current_theme: ThemeConfig = ThemeConfig()
    _theme_stack: List[ThemeConfig] = []

    @classmethod
    def get_current_theme(cls) -> ThemeConfig:
        """Get the current theme."""
        return cls._current_theme

    @classmethod
    def set_theme(cls, theme: ThemeConfig) -> None:
        """Set a new theme."""
        cls._theme_stack.append(cls._current_theme)
        cls._current_theme = theme

    @classmethod
    def reset_theme(cls) -> None:
        """Reset to previous theme."""
        if cls._theme_stack:
            cls._current_theme = cls._theme_stack.pop()

    @classmethod
    def get_color(cls, color_name: str) -> Optional[str]:
        """Get a color from the current theme."""
        colors = cls._current_theme.colors
        return getattr(colors, color_name, None)

    @classmethod
    def resolve_color(cls, color: str) -> str:
        """Resolve a color name to its hex value."""
        # Check if it's a named color
        if hasattr(cls._current_theme.colors, color):
            return getattr(cls._current_theme.colors, color)

        # Check if it's already a hex color
        if color.startswith('#'):
            return color

        # Return as-is (might be a valid ANSI color)
        return color


def use_theme() -> ThemeConfig:
    """Hook to get the current theme."""
    return ThemeProvider.get_current_theme()


def use_theme_setting() -> ThemeMode:
    """Hook to get the theme mode setting."""
    return use_theme().mode


def use_preview_theme() -> Dict[str, Any]:
    """Hook to get preview theme colors."""
    theme = use_theme()
    return {
        'mode': theme.mode.value,
        'colors': {
            'background': theme.colors.background,
            'foreground': theme.colors.foreground,
            'accent': theme.colors.accent,
            'muted': theme.colors.muted,
        }
    }


# Themed component styles
def get_themed_style(
    color: Optional[str] = None,
    background_color: Optional[str] = None,
    **kwargs,
) -> Style:
    """Get a themed style."""
    style_kwargs = {}

    if color:
        style_kwargs['color'] = ThemeProvider.resolve_color(color)
    if background_color:
        style_kwargs['bgcolor'] = ThemeProvider.resolve_color(background_color)

    return Style(**style_kwargs)


# Predefined themed components (for compatibility)
class ThemedBox:
    """Themed box component."""

    def __init__(self, **styles):
        self.styles = styles

    def render(self) -> str:
        # Simple placeholder
        return ""


class ThemedText:
    """Themed text component."""

    def __init__(self, content: str = "", **styles):
        self.content = content
        self.styles = styles

    def render(self) -> str:
        style = get_themed_style(**self.styles)
        return f"[{style}]{self.content}[/]"


# Color utility
def color(color_name: str) -> str:
    """Resolve a color name to its value."""
    return ThemeProvider.resolve_color(color_name)


# Rich theme for console
def get_rich_theme() -> Theme:
    """Get a Rich Theme object."""
    theme_config = ThemeProvider.get_current_theme()
    colors = theme_config.colors

    return Theme({
        "repr.str": colors.blue,
        "repr.number": colors.cyan,
        "repr.bool": colors.yellow,
        "repr.null": colors.muted,
        "logging.level.info": colors.green,
        "logging.level.warning": colors.yellow,
        "logging.level.error": colors.red,
        "logging.level.critical": colors.red,
    })


__all__ = [
    'ThemeMode',
    'ThemeColors',
    'ThemeConfig',
    'ThemeProvider',
    'use_theme',
    'use_theme_setting',
    'use_preview_theme',
    'ThemedBox',
    'ThemedText',
    'color',
    'get_rich_theme',
]