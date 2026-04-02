"""
Worktree utilities.

Git worktree management.
"""

import os
import subprocess
from typing import Optional, List, Dict, Any


def list_worktrees() -> List[Dict[str, str]]:
    """List git worktrees.

    Returns:
        List of worktree info
    """
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        worktrees = []
        current = {}
        for line in result.stdout.split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("HEAD "):
                current["head"] = line.split(" ", 1)[1]
        if current:
            worktrees.append(current)
        return worktrees
    except Exception:
        return []


def get_current_worktree() -> Optional[str]:
    """Get current worktree path.

    Returns:
        Worktree path or None
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def is_worktree(path: str) -> bool:
    """Check if path is a worktree.

    Args:
        path: Path to check

    Returns:
        True if worktree
    """
    git_dir = os.path.join(path, ".git")
    if os.path.isfile(git_dir):
        # Could be a worktree pointer
        with open(git_dir) as f:
            content = f.read()
            return "worktrees" in content
    return False


__all__ = [
    "list_worktrees",
    "get_current_worktree",
    "is_worktree",
]