"""Tools constants."""

from typing import Dict, List


# Tool categories
TOOL_CATEGORY_FILE = 'file'
TOOL_CATEGORY_SEARCH = 'search'
TOOL_CATEGORY_EXECUTE = 'execute'
TOOL_CATEGORY_EDIT = 'edit'
TOOL_CATEGORY_OTHER = 'other'

# Tool descriptions
TOOL_DESCRIPTIONS: Dict[str, str] = {
    'bash': 'Execute shell commands',
    'read': 'Read file contents',
    'write': 'Write or create files',
    'edit': 'Edit file contents',
    'glob': 'Find files by pattern',
    'grep': 'Search file contents',
    'lsp': 'Language server protocol',
    'mcp': 'Model Context Protocol',
    'agent': 'Spawn sub-agents',
    'task': 'Manage tasks',
    'web_fetch': 'Fetch web content',
    'web_search': 'Search the web',
}

# Tool timeout defaults (seconds)
TOOL_TIMEOUTS: Dict[str, int] = {
    'bash': 120,
    'read': 30,
    'write': 30,
    'edit': 30,
    'glob': 10,
    'grep': 30,
    'lsp': 60,
    'mcp': 60,
    'web_fetch': 30,
    'web_search': 30,
}


def get_tool_description(tool_name: str) -> str:
    """Get description for a tool."""
    return TOOL_DESCRIPTIONS.get(tool_name, '')


def get_tool_timeout(tool_name: str) -> int:
    """Get timeout for a tool."""
    return TOOL_TIMEOUTS.get(tool_name, 60)


def get_tool_category(tool_name: str) -> str:
    """Get category for a tool."""
    if tool_name in ['bash', 'shell']:
        return TOOL_CATEGORY_EXECUTE
    elif tool_name in ['read', 'write', 'edit', 'glob']:
        return TOOL_CATEGORY_FILE
    elif tool_name in ['grep', 'search']:
        return TOOL_CATEGORY_SEARCH
    return TOOL_CATEGORY_OTHER


__all__ = [
    'TOOL_CATEGORY_FILE',
    'TOOL_CATEGORY_SEARCH',
    'TOOL_CATEGORY_EXECUTE',
    'TOOL_CATEGORY_EDIT',
    'TOOL_CATEGORY_OTHER',
    'TOOL_DESCRIPTIONS',
    'TOOL_TIMEOUTS',
    'get_tool_description',
    'get_tool_timeout',
    'get_tool_category',
]