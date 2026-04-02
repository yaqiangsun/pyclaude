"""
Cross project resume utilities.

Check if a log is from a different project directory and determine
whether it's a related worktree or a completely different project.
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CrossProjectResumeResult:
    """Result of cross-project resume check."""
    is_cross_project: bool
    is_same_repo_worktree: Optional[bool] = None
    project_path: Optional[str] = None
    command: Optional[str] = None


# Stub for get_original_cwd - will be imported from bootstrap/state when available
def get_original_cwd() -> str:
    """Get the original working directory."""
    return os.getcwd()


# Stub for quote - will be imported from bash utilities when available
def quote(paths: List[str]) -> str:
    """Quote paths for shell."""
    return " ".join(f'"{p}"' for p in paths)


# Stub for get_session_id_from_log - will be implemented later
def get_session_id_from_log(log: dict) -> str:
    """Get session ID from log."""
    return log.get("sessionId", log.get("session_id", ""))


def check_cross_project_resume(
    log: dict,
    show_all_projects: bool,
    worktree_paths: List[str],
) -> CrossProjectResumeResult:
    """Check if a log is from a different project directory.

    For same-repo worktrees, we can resume directly without requiring cd.
    For different projects, we generate the cd command.

    Args:
        log: The log option to check
        show_all_projects: Whether to show all projects
        worktree_paths: List of worktree paths

    Returns:
        CrossProjectResumeResult with the check results
    """
    current_cwd = get_original_cwd()

    project_path = log.get("projectPath")
    if not show_all_projects or not project_path or project_path == current_cwd:
        return CrossProjectResumeResult(is_cross_project=False)

    # Check if log.projectPath is under a worktree of the same repo
    is_same_repo = any(
        project_path == wt or project_path.startswith(wt + os.sep)
        for wt in worktree_paths
    )

    if is_same_repo:
        return CrossProjectResumeResult(
            is_cross_project=True,
            is_same_repo_worktree=True,
            project_path=project_path,
        )

    # Different repo - generate cd command
    session_id = get_session_id_from_log(log)
    command = f"cd {quote([project_path])} && claude --resume {session_id}"
    return CrossProjectResumeResult(
        is_cross_project=True,
        is_same_repo_worktree=False,
        project_path=project_path,
        command=command,
    )


__all__ = [
    "CrossProjectResumeResult",
    "check_cross_project_resume",
]