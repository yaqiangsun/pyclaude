"""
Completion cache utilities.

Generate and cache shell completion scripts.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

EOL = "\n"


@dataclass
class ShellInfo:
    """Shell information."""
    name: str
    rc_file: str
    cache_file: str
    completion_line: str
    shell_flag: str


def detect_shell() -> Optional[ShellInfo]:
    """Detect the current shell.

    Returns:
        ShellInfo or None if not detected
    """
    shell = os.environ.get("SHELL", "")
    home = str(Path.home())
    claude_dir = os.path.join(home, ".claude")

    if shell.endswith("/zsh") or shell.endswith("/zsh.exe"):
        cache_file = os.path.join(claude_dir, "completion.zsh")
        return ShellInfo(
            name="zsh",
            rc_file=os.path.join(home, ".zshrc"),
            cache_file=cache_file,
            completion_line=f'[[ -f "{cache_file}" ]] && source "{cache_file}"',
            shell_flag="zsh",
        )

    if shell.endswith("/bash") or shell.endswith("/bash.exe"):
        cache_file = os.path.join(claude_dir, "completion.bash")
        return ShellInfo(
            name="bash",
            rc_file=os.path.join(home, ".bashrc"),
            cache_file=cache_file,
            completion_line=f'[ -f "{cache_file}" ] && source "{cache_file}"',
            shell_flag="bash",
        )

    if shell.endswith("/fish") or shell.endswith("/fish.exe"):
        xdg_config = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
        cache_file = os.path.join(claude_dir, "completion.fish")
        return ShellInfo(
            name="fish",
            rc_file=os.path.join(xdg_config, "fish", "config.fish"),
            cache_file=cache_file,
            completion_line=f'[ -f "{cache_file}" ] && source "{cache_file}"',
            shell_flag="fish",
        )

    return None


def format_path_link(file_path: str) -> str:
    """Format path as a clickable link if supported."""
    return file_path


async def setup_shell_completion(theme: str = "default") -> str:
    """Generate and cache completion script, add source line to shell rc file.

    Args:
        theme: Theme name

    Returns:
        Status message
    """
    shell = detect_shell()
    if not shell:
        return ""

    # Ensure the cache directory exists
    cache_dir = os.path.dirname(shell.cache_file)
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except Exception as e:
        return f"{EOL}Warning: Could not write {shell.name} completion cache{EOL}Run manually: claude completion {shell.shell_flag} > {shell.cache_file}{EOL}"

    # Generate the completion script
    claude_bin = "claude"
    result = subprocess.run(
        [claude_bin, "completion", shell.shell_flag, "--output", shell.cache_file],
        capture_output=True,
    )
    if result.returncode != 0:
        return f"{EOL}Warning: Could not generate {shell.name} shell completions{EOL}"

    # Check if rc file already sources completions
    existing = ""
    try:
        if os.path.exists(shell.rc_file):
            with open(shell.rc_file, "r") as f:
                existing = f.read()
        if "claude completion" in existing or shell.cache_file in existing:
            return f"{EOL}Shell completions updated for {shell.name}{EOL}"
    except Exception:
        pass

    # Append source line to rc file
    try:
        config_dir = os.path.dirname(shell.rc_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)

        separator = "" if existing.endswith("\n") else "\n"
        content = f"{existing}{separator}\n# Claude Code shell completions\n{shell.completion_line}\n"
        with open(shell.rc_file, "w") as f:
            f.write(content)

        return f"{EOL}Installed {shell.name} shell completions{EOL}"
    except Exception:
        return f"{EOL}Warning: Could not install {shell.name} shell completions{EOL}"


async def regenerate_completion_cache() -> None:
    """Regenerate cached shell completion scripts."""
    shell = detect_shell()
    if not shell:
        return

    claude_bin = "claude"
    result = subprocess.run(
        [claude_bin, "completion", shell.shell_flag, "--output", shell.cache_file],
        capture_output=True,
    )
    if result.returncode != 0:
        return


__all__ = [
    "ShellInfo",
    "detect_shell",
    "setup_shell_completion",
    "regenerate_completion_cache",
]