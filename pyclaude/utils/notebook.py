"""
Notebook utilities.

Jupyter notebook handling.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


def is_notebook(path: str) -> bool:
    """Check if file is a Jupyter notebook.

    Args:
        path: File path

    Returns:
        True if notebook
    """
    return path.endswith('.ipynb')


def parse_notebook(path: str) -> Optional[Dict[str, Any]]:
    """Parse Jupyter notebook.

    Args:
        path: Notebook path

    Returns:
        Notebook dict or None
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def get_notebook_cells(path: str) -> List[Dict[str, Any]]:
    """Get cells from notebook.

    Args:
        path: Notebook path

    Returns:
        List of cells
    """
    notebook = parse_notebook(path)
    if notebook and "cells" in notebook:
        return notebook["cells"]
    return []


def extract_code_from_notebook(path: str) -> List[str]:
    """Extract all code cells from notebook.

    Args:
        path: Notebook path

    Returns:
        List of code strings
    """
    cells = get_notebook_cells(path)
    return [cell.get("source", "") for cell in cells if cell.get("cell_type") == "code"]


__all__ = [
    "is_notebook",
    "parse_notebook",
    "get_notebook_cells",
    "extract_code_from_notebook",
]