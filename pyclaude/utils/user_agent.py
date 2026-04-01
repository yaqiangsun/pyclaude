"""
User-Agent string helpers.

Kept dependency-free so SDK-bundled code (bridge, cli/transports) can
import without pulling in auth.ts and its transitive dependency tree.
"""

import os

# Version would normally be set at build time
VERSION = os.environ.get("CLAUDE_CODE_VERSION", "0.1.0")


def get_claude_code_user_agent() -> str:
    """Returns the User-Agent string for Claude Code."""
    return f"claude-code/{VERSION}"