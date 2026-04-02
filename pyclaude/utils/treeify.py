"""
Treeify utilities.

Convert flat structures to trees.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TreeNode:
    """A node in a tree."""
    value: Any
    children: List["TreeNode"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


def treeify(
    items: List[Dict[str, Any]],
    key: str = "id",
    parent_key: str = "parent_id",
) -> List[TreeNode]:
    """Convert flat list to tree.

    Args:
        items: Flat list of items
        key: Key for node identity
        parent_key: Key for parent reference

    Returns:
        List of root nodes
    """
    if not items:
        return []

    # Build lookup
    nodes: Dict[str, TreeNode] = {}
    roots: List[TreeNode] = []

    # First pass: create all nodes
    for item in items:
        nodes[item[key]] = TreeNode(value=item)

    # Second pass: link parents and children
    for item in items:
        node = nodes[item[key]]
        parent_id = item.get(parent_key)

        if parent_id and parent_id in nodes:
            nodes[parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


def tree_to_text(tree: TreeNode, indent: int = 0, prefix: str = "") -> str:
    """Convert tree to text representation.

    Args:
        tree: Root node
        indent: Current indent level
        prefix: Prefix for connector lines

    Returns:
        Tree as text
    """
    lines = []
    connector = "└── " if indent > 0 else ""
    lines.append(prefix + connector + str(tree.value))

    for i, child in enumerate(tree.children):
        child_prefix = prefix + ("    " if i == len(tree.children) - 1 else "│   ")
        lines.append(tree_to_text(child, indent + 1, child_prefix))

    return "\n".join(lines)


__all__ = [
    "TreeNode",
    "treeify",
    "tree_to_text",
]