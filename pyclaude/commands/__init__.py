"""Commands package."""

from typing import Any, Dict

# Import command modules
from .help import call as help_call, AVAILABLE_COMMANDS
from .clear import call as clear_call
from .compact import call as compact_call, is_enabled as compact_enabled
from .commit import call as commit_call, CONFIG as COMMIT_CONFIG
from .resume import call as resume_call
from .version import call as version_call
from .status import call as status_call
from .btw import call as btw_call
from .init import call as init_call

# Import from command packages
try:
    from .exit import call as exit_call, CONFIG as EXIT_CONFIG
except ImportError:
    exit_call = None
    EXIT_CONFIG = {'name': 'exit', 'description': 'Exit Claude Code', 'aliases': ['quit', 'q']}

try:
    from .session import call as session_call, CONFIG as SESSION_CONFIG
except ImportError:
    session_call = None
    SESSION_CONFIG = {'name': 'session', 'description': 'Manage sessions'}

try:
    from .model import call as model_call, CONFIG as MODEL_CONFIG
except ImportError:
    model_call = None
    MODEL_CONFIG = {'name': 'model', 'description': 'Switch models'}

try:
    from .config import call as config_call, CONFIG as CONFIG_CMD_CONFIG
except ImportError:
    config_call = None
    CONFIG_CMD_CONFIG = {'name': 'config', 'description': 'Manage settings'}

try:
    from .mcp import call as mcp_call, CONFIG as MCP_CONFIG
except ImportError:
    mcp_call = None
    MCP_CONFIG = {'name': 'mcp', 'description': 'Manage MCP servers'}

try:
    from .skills import call as skills_call, CONFIG as SKILLS_CONFIG
except ImportError:
    skills_call = None
    SKILLS_CONFIG = {'name': 'skills', 'description': 'Manage skills'}

try:
    from .plugins import call as plugins_call, CONFIG as PLUGINS_CONFIG
except ImportError:
    plugins_call = None
    PLUGINS_CONFIG = {'name': 'plugins', 'description': 'Manage plugins'}

try:
    from .theme import call as theme_call, CONFIG as THEME_CONFIG
except ImportError:
    theme_call = None
    THEME_CONFIG = {'name': 'theme', 'description': 'Change theme'}

try:
    from .fast import call as fast_call, CONFIG as FAST_CONFIG
except ImportError:
    fast_call = None
    FAST_CONFIG = {'name': 'fast', 'description': 'Toggle fast mode'}

try:
    from .doctor import call as doctor_call, CONFIG as DOCTOR_CONFIG
except ImportError:
    doctor_call = None
    DOCTOR_CONFIG = {'name': 'doctor', 'description': 'Run diagnostics'}

try:
    from .cost import call as cost_call, CONFIG as COST_CONFIG
except ImportError:
    cost_call = None
    COST_CONFIG = {'name': 'cost', 'description': 'Show cost'}

try:
    from .stats import call as stats_call, CONFIG as STATS_CONFIG
except ImportError:
    stats_call = None
    STATS_CONFIG = {'name': 'stats', 'description': 'Show statistics'}

try:
    from .diff import call as diff_call, CONFIG as DIFF_CONFIG
except ImportError:
    diff_call = None
    DIFF_CONFIG = {'name': 'diff', 'description': 'Show git diff'}

try:
    from .files import call as files_call, CONFIG as FILES_CONFIG
except ImportError:
    files_call = None
    FILES_CONFIG = {'name': 'files', 'description': 'Manage files'}

try:
    from .login import call as login_call, CONFIG as LOGIN_CONFIG
except ImportError:
    login_call = None
    LOGIN_CONFIG = {'name': 'login', 'description': 'Login'}

# Command registry
COMMANDS: Dict[str, Any] = {
    'help': {'call': help_call, 'description': 'Show help'},
    'clear': {'call': clear_call, 'description': 'Clear conversation'},
    'compact': {'call': compact_call, 'description': 'Compact conversation'},
    'commit': {'call': commit_call, 'description': 'Create git commit'},
    'resume': {'call': resume_call, 'description': 'Resume session'},
    'version': {'call': version_call, 'description': 'Show version'},
    'status': {'call': status_call, 'description': 'Show session status'},
    'btw': {'call': btw_call, 'description': 'Add side note'},
    'init': {'call': init_call, 'description': 'Initialize project'},
}

# Add commands that have implementations
if exit_call:
    COMMANDS['exit'] = {'call': exit_call, 'description': 'Exit Claude Code', 'aliases': ['quit', 'q']}
if session_call:
    COMMANDS['session'] = {'call': session_call, 'description': 'Manage sessions'}
if model_call:
    COMMANDS['model'] = {'call': model_call, 'description': 'Switch models'}
if config_call:
    COMMANDS['config'] = {'call': config_call, 'description': 'Manage settings'}
if mcp_call:
    COMMANDS['mcp'] = {'call': mcp_call, 'description': 'Manage MCP servers'}
if skills_call:
    COMMANDS['skills'] = {'call': skills_call, 'description': 'Manage skills'}
if plugins_call:
    COMMANDS['plugins'] = {'call': plugins_call, 'description': 'Manage plugins'}
if theme_call:
    COMMANDS['theme'] = {'call': theme_call, 'description': 'Change theme'}
if fast_call:
    COMMANDS['fast'] = {'call': fast_call, 'description': 'Toggle fast mode'}
if doctor_call:
    COMMANDS['doctor'] = {'call': doctor_call, 'description': 'Run diagnostics'}
if cost_call:
    COMMANDS['cost'] = {'call': cost_call, 'description': 'Show cost'}
if stats_call:
    COMMANDS['stats'] = {'call': stats_call, 'description': 'Show statistics'}
if diff_call:
    COMMANDS['diff'] = {'call': diff_call, 'description': 'Show git diff'}
if files_call:
    COMMANDS['files'] = {'call': files_call, 'description': 'Manage files'}
if login_call:
    COMMANDS['login'] = {'call': login_call, 'description': 'Login'}

def get_all_commands() -> list:
    """Get all available commands."""
    return list(COMMANDS.values())


__all__ = [
    # Local commands
    'COMMANDS',
    'get_all_commands',
    'help_call',
    'clear_call',
    'compact_call',
    'commit_call',
    'resume_call',
    'version_call',
    'status_call',
    'btw_call',
    'init_call',
    'AVAILABLE_COMMANDS',
]