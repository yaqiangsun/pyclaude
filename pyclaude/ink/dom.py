"""
Ink DOM - Document Object Model for terminal rendering.
"""
from typing import Optional, List, Any, Dict
from dataclasses import dataclass, field
from enum import Enum
from .styles import Styles


class NodeType(Enum):
    """DOM node types."""
    TEXT = "text"
    BOX = "box"
    FRAGMENT = "fragment"


@dataclass
class DOMNode:
    """Base DOM node."""
    node_type: NodeType
    styles: Styles = field(default_factory=Styles)
    children: List['DOMNode'] = field(default_factory=list)
    parent: Optional['DOMNode'] = None

    def append_child(self, child: 'DOMNode') -> None:
        """Append a child node."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'DOMNode') -> None:
        """Remove a child node."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def insert_before(self, new_child: 'DOMNode', ref_child: 'DOMNode') -> None:
        """Insert a child before a reference child."""
        if ref_child in self.children:
            idx = self.children.index(ref_child)
            new_child.parent = self
            self.children.insert(idx, new_child)

    def get_text_content(self) -> str:
        """Get text content of this node and children."""
        if self.node_type == NodeType.TEXT:
            return self._text_content or ""
        return "".join(child.get_text_content() for child in self.children)


@dataclass
class TextNode(DOMNode):
    """Text node."""
    node_type: NodeType = NodeType.TEXT
    _text_content: str = ""

    def __init__(self, content: str = ""):
        super().__init__(node_type=NodeType.TEXT)
        self._text_content = content


@dataclass
class ElementNode(DOMNode):
    """Element node (like Box)."""
    node_type: NodeType = NodeType.BOX
    tag_name: str = ""

    def __init__(self, tag_name: str, styles: Styles = None):
        super().__init__(node_type=NodeType.BOX if tag_name else NodeType.FRAGMENT)
        self.tag_name = tag_name
        if styles:
            self.styles = styles


class DOMElement(DOMNode):
    """DOM element (alias for ElementNode for compatibility)."""

    def __init__(self, tag_name: str = "", styles: Styles = None):
        super().__init__(
            node_type=NodeType.BOX if tag_name else NodeType.FRAGMENT,
            styles=styles or Styles(),
        )
        self.tag_name = tag_name


# DOM tree
class DOM:
    """DOM tree container."""

    def __init__(self):
        self.root: Optional[DOMNode] = None
        self._focused_node: Optional[DOMNode] = None

    def set_root(self, root: DOMNode) -> None:
        """Set the root node."""
        self.root = root

    def get_focused_node(self) -> Optional[DOMNode]:
        """Get the currently focused node."""
        return self._focused_node

    def set_focused_node(self, node: Optional[DOMNode]) -> None:
        """Set the focused node."""
        self._focused_node = node


# Global DOM instance
_dom: Optional[DOM] = None


def get_dom() -> DOM:
    """Get the global DOM instance."""
    global _dom
    if _dom is None:
        _dom = DOM()
    return _dom


def create_element(tag: str, props: Dict[str, Any] = None, *children) -> ElementNode:
    """Create a DOM element (React-like API)."""
    styles = Styles()
    if props:
        # Extract style-related props
        for key, value in props.items():
            if hasattr(styles, key):
                setattr(styles, key, value)

    element = ElementNode(tag_name=tag, styles=styles)

    # Add children
    for child in children:
        if isinstance(child, DOMNode):
            element.append_child(child)
        elif isinstance(child, str):
            element.append_child(TextNode(content=child))

    return element


def create_text_element(text: str) -> TextNode:
    """Create a text element."""
    return TextNode(content=text)


__all__ = [
    'NodeType',
    'DOMNode',
    'TextNode',
    'ElementNode',
    'DOMElement',
    'DOM',
    'get_dom',
    'create_element',
    'create_text_element',
]