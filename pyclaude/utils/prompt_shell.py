"""
Prompt shell execution utilities.

Shell prompt handling.
"""

import os
import subprocess
from typing import Optional, List


def get_shell_prompt() -> str:
    """Get current shell prompt.

    Returns:
        Prompt string
    """
    return os.environ.get("PS1", "$ ")


def get_shell_type() -> str:
    """Get shell type.

    Returns:
        Shell name (bash, zsh, etc.)
    """
    shell = os.environ.get("SHELL", "")
    return os.path.basename(shell)


def detect_shell() -> str:
    """Detect available shell.

    Returns:
        Shell path
    """
    for shell in ["/bin/bash", "/bin/zsh", "/bin/sh"]:
        if os.path.exists(shell):
            return shell
    return "/bin/sh"


def run_shell_command(
    command: str,
    cwd: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """Run shell command.

    Args:
        command: Command to run
        cwd: Working directory

    Returns:
        Completed process
    """
    shell = get_shell_type()
    return subprocess.run(
        command,
        shell=True,
        executable=detect_shell(),
        cwd=cwd,
        capture_output=True,
        text=True,
    )


__all__ = [
    "get_shell_prompt",
    "get_shell_type",
    "detect_shell",
    "run_shell_command",
]