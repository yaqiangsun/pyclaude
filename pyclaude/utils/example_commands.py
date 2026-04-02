"""
Example command utilities.

Provides example command suggestions based on frequently modified files.
"""

import re
import os
import random
from typing import List, Optional
from functools import lru_cache
from collections import Counter

# Patterns that mark a file as non-core (auto-generated, dependency, or config)
NON_CORE_PATTERNS = [
    # lock / dependency manifests
    re.compile(r"(?:^|\/)(?:package-lock\.json|yarn\.lock|bun\.lock|bun\.lockb|pnpm-lock\.yaml|Pipfile\.lock|poetry\.lock|Cargo\.lock|Gemfile\.lock|go\.sum|composer\.lock|uv\.lock)$"),
    # generated / build artifacts
    re.compile(r"\.generated\."),
    re.compile(r"(?:^|\/)(?:dist|build|out|target|node_modules|\.next|__pycache__)\/"),
    re.compile(r"\.(?:min\.js|min\.css|map|pyc|pyo)$"),
    # data / docs / config extensions
    re.compile(r"\.(?:json|ya?ml|toml|xml|ini|cfg|conf|env|lock|txt|md|mdx|rst|csv|log|svg)$", re.IGNORECASE),
    # configuration / metadata
    re.compile(r"(?:^|\/)\.?(?:eslintrc|prettierrc|babelrc|editorconfig|gitignore|gitattributes|dockerignore|npmrc)"),
    re.compile(r"(?:^|\/)(?:tsconfig|jsconfig|biome|vitest\.config|jest\.config|webpack\.config|vite\.config|rollup\.config)\.[a-z]+$"),
    re.compile(r"(?:^|\/)\.(?:github|vscode|idea|claude)\/"),
    # docs / changelogs
    re.compile(r"(?:^|\/)(?:CHANGELOG|LICENSE|CONTRIBUTING|CODEOWNERS|README)(?:\.[a-z]+)?$", re.IGNORECASE),
]


def _is_core_file(path: str) -> bool:
    """Check if a file is a core file (not auto-generated, dependency, or config)."""
    return not any(p.search(path) for p in NON_CORE_PATTERNS)


def count_and_sort_items(items: List[str], top_n: int = 20) -> str:
    """Count occurrences and return top N items sorted by count.

    Args:
        items: List of items to count
        top_n: Number of top items to return

    Returns:
        Formatted string with counts and items
    """
    counts = Counter(items)
    return "\n".join(
        f"{count:6} {item}"
        for item, count in counts.most_common(top_n)
    )


def pick_diverse_core_files(sorted_paths: List[str], want: int) -> List[str]:
    """Pick up to `want` basenames from a frequency-sorted list.

    Skips non-core files and spreads across different directories.

    Args:
        sorted_paths: Paths sorted by frequency
        want: Number of files to pick

    Returns:
        List of picked basenames, or empty if fewer than want available
    """
    picked = []
    seen_basenames = set()
    dir_tally = {}

    # Greedy: on each pass allow +1 file per directory
    for cap in range(1, want + 1):
        if len(picked) >= want:
            break
        for p in sorted_paths:
            if len(picked) >= want:
                break
            if not _is_core_file(p):
                continue

            # Get basename
            last_sep = max(p.rfind("/"), p.rfind("\\"))
            base = p[last_sep + 1:] if last_sep >= 0 else p
            if not base or base in seen_basenames:
                continue

            # Get directory
            dir_path = p[:last_sep] if last_sep >= 0 else "."
            if dir_tally.get(dir_path, 0) >= cap:
                continue

            picked.append(base)
            seen_basenames.add(base)
            dir_tally[dir_path] = dir_tally.get(dir_path, 0) + 1

    return picked if len(picked) >= want else []


async def get_frequently_modified_files() -> List[str]:
    """Get frequently modified files in the repository.

    Returns:
        List of frequently modified file basenames
    """
    # Skip in test mode or on Windows
    if os.environ.get("NODE_ENV") == "test":
        return []
    if os.name == "nt":
        return []

    # Check if git repo
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
    except Exception:
        return []

    try:
        # Get user email if available
        user_email = None
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                user_email = result.stdout.strip()
        except Exception:
            pass

        log_args = [
            "log",
            "-n", "1000",
            "--pretty=format:",
            "--name-only",
            "--diff-filter=M",
        ]

        counts = {}

        if user_email:
            result = subprocess.run(
                ["git"] + log_args + [f"--author={user_email}"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            for line in result.stdout.split("\n"):
                f = line.strip()
                if f:
                    counts[f] = counts.get(f, 0) + 1

        # Fall back to all authors if history is thin
        if len(counts) < 10:
            result = subprocess.run(
                ["git"] + log_args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            for line in result.stdout.split("\n"):
                f = line.strip()
                if f:
                    counts[f] = counts.get(f, 0) + 1

        sorted_paths = sorted(counts.keys(), key=lambda p: counts[p], reverse=True)
        return pick_diverse_core_files(sorted_paths, 5)
    except Exception:
        return []


ONE_WEEK_IN_MS = 7 * 24 * 60 * 60 * 1000

# Placeholder for project config
def _get_project_config() -> dict:
    return {}


def _save_project_config(config: dict) -> None:
    pass


@lru_cache(maxsize=1)
def get_example_command() -> str:
    """Get a random example command.

    Returns:
        Example command string
    """
    project_config = _get_project_config()
    frequent_file = random.choice(project_config.get("exampleFiles", [""]))

    commands = [
        "fix lint errors",
        "fix typecheck errors",
        f"how does {frequent_file} work?",
        f"refactor {frequent_file}",
        "how do I log an error?",
        f"edit {frequent_file} to...",
        f"write a test for {frequent_file}",
        "create a util logging.py that...",
    ]

    return f'Try "{random.choice(commands)}"'


async def refresh_example_commands() -> None:
    """Refresh example commands if they're outdated."""
    project_config = _get_project_config()
    now = int(os.time.time() * 1000)
    last_generated = project_config.get("exampleFilesGeneratedAt", 0)

    # Regenerate examples if over a week old
    if now - last_generated > ONE_WEEK_IN_MS:
        project_config["exampleFiles"] = []

    # If no example files cached, kickstart fetch in background
    if not project_config.get("exampleFiles"):
        files = await get_frequently_modified_files()
        if files:
            _save_project_config({
                **project_config,
                "exampleFiles": files,
                "exampleFilesGeneratedAt": now,
            })


__all__ = [
    "count_and_sort_items",
    "pick_diverse_core_files",
    "get_example_command",
    "refresh_example_commands",
]