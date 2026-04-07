# REPL Tool Constants
# Reference: src/tools/REPLTool/constants.ts

import os


REPL_TOOL_NAME = "REPL"


def is_repl_mode_enabled() -> bool:
    """Check if REPL mode is enabled"""
    # Check environment variables
    if os.environ.get('CLAUDE_CODE_REPL') in ('0', 'false', 'no'):
        return False
    if os.environ.get('CLAUDE_REPL_MODE') in ('1', 'true', 'yes'):
        return True

    # Check if running as ant in CLI mode
    user_type = os.environ.get('USER_TYPE', '')
    entrypoint = os.environ.get('CLAUDE_CODE_ENTRYPOINT', '')
    return user_type == 'ant' and entrypoint == 'cli'


# Tools that are only accessible via REPL when REPL mode is enabled
REPL_ONLY_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Bash",
    "NotebookEdit",
    "Agent",
}