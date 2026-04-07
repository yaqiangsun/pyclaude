"""MCP command - manage Model Context Protocol servers."""

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

MCP_DIR = Path.home() / '.claude' / 'mcp'
MCP_PID_DIR = Path.home() / '.claude' / 'mcp' / 'pids'
DEFAULT_TOOLS = ['Bash', 'Read', 'Edit', 'Write', 'Glob', 'Grep']


def ensure_dirs():
    """Ensure MCP directories exist."""
    MCP_DIR.mkdir(parents=True, exist_ok=True)
    MCP_PID_DIR.mkdir(parents=True, exist_ok=True)


def load_server_config(name: str) -> Optional[Dict[str, Any]]:
    """Load MCP server configuration."""
    config_file = MCP_DIR / f'{name}.json'
    if not config_file.exists():
        return None
    try:
        with open(config_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_server_config(name: str, config: Dict[str, Any]) -> None:
    """Save MCP server configuration."""
    ensure_dirs()
    config_file = MCP_DIR / f'{name}.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def get_pid_file(name: str) -> Path:
    """Get the PID file for a server."""
    return MCP_PID_DIR / f'{name}.pid'


def save_pid(name: str, pid: int) -> None:
    """Save server process ID."""
    ensure_dirs()
    pid_file = get_pid_file(name)
    with open(pid_file, 'w') as f:
        f.write(str(pid))


def load_pid(name: str) -> Optional[int]:
    """Load server process ID."""
    pid_file = get_pid_file(name)
    if not pid_file.exists():
        return None
    try:
        with open(pid_file) as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return None


def remove_pid(name: str) -> None:
    """Remove server PID file."""
    pid_file = get_pid_file(name)
    if pid_file.exists():
        pid_file.unlink()


def is_process_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def parse_mcp_args(args: str) -> Dict[str, Any]:
    """Parse MCP command arguments."""
    args = args.strip()
    parts = args.split()

    if not args or parts[0] == 'list':
        return {'type': 'list'}

    if parts[0] == 'add':
        if len(parts) < 2:
            return {'type': 'add'}
        name = parts[1]
        command = ' '.join(parts[2:]) if len(parts) > 2 else ''
        return {'type': 'add', 'name': name, 'command': command}

    if parts[0] in ('remove', 'delete'):
        if len(parts) < 2:
            return {'type': 'remove'}
        return {'type': 'remove', 'name': parts[1]}

    if parts[0] == 'start':
        if len(parts) < 2:
            return {'type': 'start'}
        return {'type': 'start', 'name': parts[1]}

    if parts[0] == 'stop':
        if len(parts) < 2:
            return {'type': 'stop'}
        return {'type': 'stop', 'name': parts[1]}

    if parts[0] == 'get':
        if len(parts) < 2:
            return {'type': 'get'}
        return {'type': 'get', 'name': parts[1]}

    return {'type': 'unknown'}


async def execute(args: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the mcp command."""
    parsed = parse_mcp_args(args)
    cmd_type = parsed.get('type')

    if cmd_type == 'list':
        return await list_mcp_servers()

    if cmd_type == 'add':
        if not parsed.get('name'):
            return {'type': 'text', 'value': 'Usage: /mcp add <name> <command> [args...]'}
        return await add_mcp_server(parsed['name'], parsed.get('command', ''))

    if cmd_type == 'remove':
        if not parsed.get('name'):
            return {'type': 'text', 'value': 'Usage: /mcp remove <name>'}
        return await remove_mcp_server(parsed['name'])

    if cmd_type == 'start':
        if not parsed.get('name'):
            return {'type': 'text', 'value': 'Usage: /mcp start <name>'}
        return await start_mcp_server(parsed['name'])

    if cmd_type == 'stop':
        if not parsed.get('name'):
            return {'type': 'text', 'value': 'Usage: /mcp stop <name>'}
        return await stop_mcp_server(parsed['name'])

    if cmd_type == 'get':
        if not parsed.get('name'):
            return {'type': 'text', 'value': 'Usage: /mcp get <name>'}
        return await get_mcp_server(parsed['name'])

    return show_help()


def show_help() -> Dict[str, Any]:
    """Show help message."""
    return {'type': 'text', 'value': '''Usage: /mcp [command]

Commands:
  list              - List all MCP servers
  add <name> <cmd> - Add an MCP server (stdio type)
  remove <name>    - Remove an MCP server
  start <name>     - Start an MCP server
  stop <name>      - Stop an MCP server
  get <name>       - Show MCP server details
'''}


async def list_mcp_servers() -> Dict[str, Any]:
    """List all MCP servers."""
    ensure_dirs()

    servers = []
    for f in MCP_DIR.glob('*.json'):
        if f.stem == 'pids':
            continue
        try:
            with open(f) as fp:
                data = json.load(fp)
                servers.append({
                    'name': f.stem,
                    'command': data.get('command', ''),
                    'args': data.get('args', []),
                    'env': data.get('env', {}),
                    'enabled': data.get('enabled', True),
                })
        except Exception:
            pass

    if not servers:
        return {'type': 'text', 'value': 'No MCP servers configured.\n\nUse /mcp add <name> <command> to add one.\nExample: /mcp add myserver npx -y @modelcontextprotocol/server-filesystem /tmp'}

    lines = ['MCP Servers:', '']
    for s in sorted(servers, key=lambda x: x['name']):
        # Check if running
        pid = load_pid(s['name'])
        is_running = pid and is_process_running(pid)
        status = 'running' if is_running else 'stopped'

        cmd = s['command']
        args = s.get('args', [])
        if args:
            cmd = f'{cmd} {" ".join(args)}'

        lines.append(f'  {s["name"]}: {cmd}')
        lines.append(f'    Status: {status}')
        if is_running:
            lines.append(f'    PID: {pid}')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def get_mcp_server(name: str) -> Dict[str, Any]:
    """Show MCP server details."""
    config = load_server_config(name)

    if not config:
        return {'type': 'text', 'value': f'MCP server "{name}" not found.'}

    pid = load_pid(name)
    is_running = pid and is_process_running(pid)

    lines = [f'{name}:', f'  Type: stdio']

    cmd = config.get('command', '')
    args = config.get('args', [])
    if args:
        lines.append(f'  Command: {cmd}')
        lines.append(f'  Args: {" ".join(args)}')
    else:
        lines.append(f'  Command: {cmd}')

    if config.get('env'):
        lines.append('  Environment:')
        for k, v in config['env'].items():
            lines.append(f'    {k}={v}')

    lines.append(f'  Status: {"running" if is_running else "stopped"}')
    if is_running:
        lines.append(f'  PID: {pid}')
    elif pid:
        lines.append('  (stale PID file, server not running)')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def add_mcp_server(name: str, command: str) -> Dict[str, Any]:
    """Add an MCP server."""
    if not command:
        return {'type': 'text', 'value': 'Usage: /mcp add <name> <command> [args...]'}

    # Parse command and args
    parts = command.split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    config = {
        'command': cmd,
        'args': args,
        'enabled': True,
        'timeout': 30000,
        'type': 'stdio',
    }

    save_server_config(name, config)
    return {'type': 'text', 'value': f'Added MCP server "{name}": {cmd} {" ".join(args)}'}


async def remove_mcp_server(name: str) -> Dict[str, Any]:
    """Remove an MCP server."""
    config = load_server_config(name)

    if not config:
        return {'type': 'text', 'value': f'MCP server "{name}" not found.'}

    # Stop if running
    pid = load_pid(name)
    if pid and is_process_running(pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    remove_pid(name)

    # Remove config
    config_file = MCP_DIR / f'{name}.json'
    config_file.unlink()

    return {'type': 'text', 'value': f'Removed MCP server "{name}"'}


async def start_mcp_server(name: str) -> Dict[str, Any]:
    """Start an MCP server."""
    config = load_server_config(name)

    if not config:
        return {'type': 'text', 'value': f'MCP server "{name}" not found.'}

    # Check if already running
    pid = load_pid(name)
    if pid and is_process_running(pid):
        return {'type': 'text', 'value': f'MCP server "{name}" is already running (PID: {pid})'}

    # Start the process
    command = config.get('command', '')
    args = config.get('args', [])
    env = config.get('env', {})

    if not command:
        return {'type': 'text', 'value': f'MCP server "{name}" has no command configured.'}

    try:
        # Merge env with current environment
        full_env = os.environ.copy()
        full_env.update(env)

        # Start process
        proc = subprocess.Popen(
            [command] + args,
            env=full_env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        save_pid(name, proc.pid)

        return {'type': 'text', 'value': f'Started MCP server "{name}" (PID: {proc.pid})'}
    except Exception as e:
        return {'type': 'text', 'value': f'Failed to start MCP server "{name}": {str(e)}'}


async def stop_mcp_server(name: str) -> Dict[str, Any]:
    """Stop an MCP server."""
    config = load_server_config(name)

    if not config:
        return {'type': 'text', 'value': f'MCP server "{name}" not found.'}

    pid = load_pid(name)

    if not pid or not is_process_running(pid):
        # Clean up stale PID file
        if pid:
            remove_pid(name)
        return {'type': 'text', 'value': f'MCP server "{name}" is not running.'}

    try:
        os.kill(pid, signal.SIGTERM)
        # Give it a moment to terminate
        time.sleep(0.5)
        if is_process_running(pid):
            os.kill(pid, signal.SIGKILL)
        remove_pid(name)
        return {'type': 'text', 'value': f'Stopped MCP server "{name}"'}
    except OSError as e:
        remove_pid(name)
        return {'type': 'text', 'value': f'Error stopping MCP server "{name}": {str(e)}'}


# Command metadata
CONFIG = {
    'type': 'local',
    'name': 'mcp',
    'description': 'Manage Model Context Protocol servers',
    'supports_non_interactive': True,
}


call = execute