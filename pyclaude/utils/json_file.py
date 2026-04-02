"""
JSON utilities.

JSON file operations.
"""

import json
import os
from typing import Any, Optional


def read_json_file(path: str) -> Optional[Any]:
    """Read JSON file.

    Args:
        path: File path

    Returns:
        Parsed JSON or None
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def write_json_file(path: str, data: Any, indent: int = 2) -> bool:
    """Write JSON to file.

    Args:
        path: File path
        data: Data to write
        indent: Indentation

    Returns:
        True if successful
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception:
        return False


__all__ = [
    "read_json_file",
    "write_json_file",
]