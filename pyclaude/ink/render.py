"""
Ink render - Core rendering logic for terminal output.
"""
from typing import Optional, List, Any, Dict
from rich.console import Console, ConsoleOptions
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from .dom import DOMNode, TextNode, ElementNode, NodeType
from .styles import Styles, Color
from .string_width import string_width


class RenderContext:
    """Context for rendering."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.x: int = 0
        self.y: int = 0
        self.width: int = 80
        self.height: int = 24


class Renderer:
    """Renderer for ink nodes."""

    def __init__(self, context: Optional[RenderContext] = None):
        self.context = context or RenderContext()
        self.output: List[str] = []

    def render(self, node: DOMNode) -> str:
        """Render a DOM node to string."""
        if node.node_type == NodeType.TEXT:
            return self._render_text(node)
        elif node.node_type == NodeType.BOX:
            return self._render_box(node)
        elif node.node_type == NodeType.FRAGMENT:
            return self._render_fragment(node)
        return ""

    def _render_text(self, node: TextNode) -> str:
        """Render a text node."""
        return node.get_text_content()

    def _render_box(self, node: ElementNode) -> str:
        """Render a box element."""
        # Get styles
        styles = node.styles

        # Render children
        children_output = ""
        for child in node.children:
            children_output += self.render(child)

        # Apply border if needed
        has_border = styles.border_top > 0 or styles.border_right > 0
        if has_border:
            border_char = self._get_border_char(styles.border_style)
            border_style = self._get_border_style(styles.border_color)
            return Panel(
                children_output,
                border_style=border_style,
                box=border_char,
            )

        return children_output

    def _render_fragment(self, node: DOMNode) -> str:
        """Render a fragment (collection of nodes)."""
        output = ""
        for child in node.children:
            output += self.render(child)
        return output

    def _get_border_char(self, style: str) -> str:
        """Get border character for style."""
        border_styles = {
            'single': 'SINGLE',
            'double': 'DOUBLE',
            'round': 'ROUNDED',
            'dashed': 'DASHED',
        }
        from rich.box import Box
        return border_styles.get(style, 'SINGLE')

    def _get_border_style(self, color: Optional[Color]) -> str:
        """Get border style."""
        if color and color.value:
            if color.type == 'ansi':
                return f"ansi({color.value})"
            elif color.type == 'hex':
                return color.value
        return ""


def render_to_string(node: DOMNode) -> str:
    """Render a node to string."""
    renderer = Renderer()
    return renderer.render(node)


def render_to_console(node: DOMNode, console: Console) -> None:
    """Render a node to console."""
    renderer = Renderer(RenderContext(console))
    output = renderer.render(node)
    console.print(output)


__all__ = ['RenderContext', 'Renderer', 'render_to_string', 'render_to_console']