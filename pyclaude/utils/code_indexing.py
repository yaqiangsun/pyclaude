"""
Code indexing utilities.

Code indexing for search.
"""

import os
from typing import List, Dict, Any, Optional


def index_file(path: str, content: str) -> Dict[str, Any]:
    """Index a file for search.

    Args:
        path: File path
        content: File content

    Returns:
        Index data
    """
    return {
        "path": path,
        "content": content,
        "size": len(content),
    }


def search_index(
    index: List[Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Search indexed files.

    Args:
        index: Index data
        query: Search query

    Returns:
        Matching entries
    """
    query_lower = query.lower()
    return [
        entry for entry in index
        if query_lower in entry.get("content", "").lower()
    ]


__all__ = [
    "index_file",
    "search_index",
]