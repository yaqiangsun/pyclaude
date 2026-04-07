"""Plugins command - manage plugins.

Matches src/cli/handlers/plugins.ts command structure:
- install/i
- uninstall
- enable
- disable
- validate
- marketplace (add/remove/update/list)
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

# Import from the new services
from pyclaude.services.plugins import schemas as plugin_schemas
from pyclaude.services.plugins.installed_plugins_manager import (
    load_installed_plugins_from_disk,
)
from pyclaude.services.plugins.marketplace_manager import (
    add_marketplace_source,
    get_marketplace,
    load_known_marketplaces_config,
    refresh_all_marketplaces,
    refresh_marketplace,
    remove_marketplace_source,
)
from pyclaude.services.plugins.plugin_operations import (
    disable_all_plugins_op,
    disable_plugin_op,
    enable_plugin_op,
    install_plugin_op,
    uninstall_plugin_op,
    update_plugin_op,
    VALID_INSTALLABLE_SCOPES,
)
from pyclaude.services.plugins.plugin_identifier import parse_plugin_identifier


# ============================================================================
# Helper Functions
# ============================================================================

PLUGINS_DIR = Path.home() / '.claude' / 'plugins'
KNOWN_MARKETPLACES_FILE = PLUGINS_DIR / 'known_marketplaces.json'
MARKETPLACES_CACHE_DIR = PLUGINS_DIR / 'marketplaces'


def get_plugins_dir() -> Path:
    """Get the plugins directory, creating it if needed."""
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    return PLUGINS_DIR


def get_marketplaces_cache_dir() -> Path:
    """Get the marketplaces cache directory."""
    MARKETPLACES_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return MARKETPLACES_CACHE_DIR


def load_known_marketplaces() -> Dict[str, Any]:
    """Load known marketplaces configuration (sync wrapper)."""
    try:
        return asyncio.run(load_known_marketplaces_config())
    except Exception:
        return {}


def save_known_marketplaces(data: Dict[str, Any]) -> None:
    """Save known marketplaces configuration (sync wrapper)."""
    get_plugins_dir()
    with open(KNOWN_MARKETPLACES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def format_source_for_display(source: Dict[str, Any]) -> str:
    """Format a MarketplaceSource for display."""
    source_type = source.get('source', '')
    if source_type == 'github':
        repo = source.get('repo', '')
        ref = source.get('ref', '')
        return f"github:{repo}{('@' + ref) if ref else ''}"
    elif source_type == 'url':
        return source.get('url', '')
    elif source_type == 'git':
        url = source.get('url', '')
        ref = source.get('ref', '')
        return f"git:{url}{('@' + ref) if ref else ''}"
    elif source_type == 'npm':
        return f"npm:{source.get('package', '')}"
    elif source_type == 'file':
        return f"file:{source.get('path', '')}"
    elif source_type == 'directory':
        return f"dir:{source.get('path', '')}"
    return 'unknown source'


# ============================================================================
# Argument Parsing
# ============================================================================

def parse_plugin_args(args: str) -> Dict[str, Any]:
    """Parse plugin subcommand arguments into structured commands.

    Matches src/commands/plugin/parseArgs.ts
    """
    args = args.strip().lower() if args else ''

    if not args:
        return {'type': 'menu'}

    parts = args.split()
    command = parts[0].lower() if parts else ''

    if command in ('help', '--help', '-h'):
        return {'type': 'help'}

    if command in ('install', 'i'):
        target = parts[1] if len(parts) > 1 else None
        if not target:
            return {'type': 'install'}

        # Check if it's in format plugin@marketplace
        if '@' in target:
            plugin, marketplace = target.split('@', 1)
            return {'type': 'install', 'plugin': plugin, 'marketplace': marketplace}

        # Check if target looks like a marketplace URL/path
        is_marketplace = (
            target.startswith('http://') or
            target.startswith('https://') or
            target.startswith('file://') or
            '/' in target or
            '\\' in target
        )

        if is_marketplace:
            return {'type': 'install', 'marketplace': target}
        return {'type': 'install', 'plugin': target}

    if command == 'manage':
        return {'type': 'manage'}

    if command == 'uninstall':
        return {'type': 'uninstall', 'plugin': parts[1] if len(parts) > 1 else None}

    if command == 'enable':
        return {'type': 'enable', 'plugin': parts[1] if len(parts) > 1 else None}

    if command == 'disable':
        # Handle --all flag
        has_all = '--all' in parts or '-a' in parts
        if has_all:
            return {'type': 'disable', 'all': True}
        return {'type': 'disable', 'plugin': parts[1] if len(parts) > 1 else None}

    if command == 'update':
        return {'type': 'update', 'plugin': parts[1] if len(parts) > 1 else None}

    if command == 'validate':
        target = ' '.join(parts[1:]).strip() if len(parts) > 1 else None
        return {'type': 'validate', 'path': target}

    if command in ('marketplace', 'market'):
        action = parts[1].lower() if len(parts) > 1 else None
        target = ' '.join(parts[2:]).strip() if len(parts) > 2 else None

        if action == 'add':
            return {'type': 'marketplace', 'action': 'add', 'target': target}
        if action in ('remove', 'rm'):
            return {'type': 'marketplace', 'action': 'remove', 'target': target}
        if action == 'update':
            return {'type': 'marketplace', 'action': 'update', 'target': target}
        if action == 'list':
            return {'type': 'marketplace', 'action': 'list'}
        return {'type': 'marketplace'}

    if command == 'list':
        # Handle list command
        return {'type': 'list'}

    # Unknown command, show menu
    return {'type': 'menu'}


# ============================================================================
# Main Execute Function
# ============================================================================

async def execute(args: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the plugins command."""
    parsed = parse_plugin_args(args)

    cmd_type = parsed.get('type', 'menu')

    if cmd_type == 'help':
        return show_help()

    if cmd_type == 'menu':
        return await show_plugin_menu()

    if cmd_type == 'list':
        return await list_plugins()

    if cmd_type == 'install':
        return await install_plugin(parsed.get('plugin'), parsed.get('marketplace'))

    if cmd_type == 'uninstall':
        return await uninstall_plugin(parsed.get('plugin'))

    if cmd_type == 'enable':
        return await enable_plugin(parsed.get('plugin'))

    if cmd_type == 'disable':
        if parsed.get('all'):
            return await disable_all_plugins()
        return await disable_plugin(parsed.get('plugin'))

    if cmd_type == 'update':
        return await update_plugin(parsed.get('plugin'))

    if cmd_type == 'validate':
        return await validate_plugin(parsed.get('path'))

    if cmd_type == 'marketplace':
        return await handle_marketplace(parsed.get('action'), parsed.get('target'))

    return show_help()


# ============================================================================
# Help
# ============================================================================

def show_help() -> Dict[str, Any]:
    """Show help message."""
    return {'type': 'text', 'value': '''Usage: /plugins [command]

Commands:
  install <plugin>           Install a plugin (or /plugins install marketplace_url)
  install <plugin>@<marketplace>  Install plugin from specific marketplace
  uninstall <plugin>         Uninstall a plugin
  enable <plugin>            Enable a plugin
  disable <plugin>           Disable a plugin
  disable --all              Disable all plugins
  update <plugin>            Update a plugin to latest version
  validate [path]            Validate a plugin
  list                       List installed plugins
  marketplace add <source>   Add a marketplace
  marketplace remove <name>  Remove a marketplace
  marketplace list           List configured marketplaces
  marketplace update         Update all marketplaces
  marketplace update <name>  Update specific marketplace

Alias: /plugin, /marketplace
'''}


# ============================================================================
# Plugin Menu / List
# ============================================================================

async def show_plugin_menu() -> Dict[str, Any]:
    """Show the plugin menu (installed plugins)."""
    plugins_result = await list_installed_plugins()
    marketplace_result = await list_marketplaces()

    lines = []

    if plugins_result.get('type') == 'text':
        lines.append(plugins_result['value'])
        lines.append('')

    if marketplace_result.get('type') == 'text':
        lines.append(marketplace_result['value'])

    return {'type': 'text', 'value': '\n'.join(lines)}


async def list_plugins() -> Dict[str, Any]:
    """List all plugins (installed)."""
    return await list_installed_plugins()


async def list_installed_plugins() -> Dict[str, Any]:
    """List installed plugins."""
    data = load_installed_plugins_from_disk()
    plugins = data.get('plugins', {})

    if not plugins:
        return {'type': 'text', 'value': 'No plugins installed.\n\nUse /plugins install <plugin> to install a plugin.'}

    lines = ['Installed plugins:', '']

    # Load settings to check enabled state
    settings_file = Path.home() / '.claude' / 'settings.json'
    enabled_plugins = {}
    if settings_file.exists():
        try:
            with open(settings_file) as f:
                settings = json.load(f)
                enabled_plugins = settings.get('enabledPlugins', {})
        except (json.JSONDecodeError, IOError):
            pass

    for plugin_id, installations in sorted(plugins.items()):
        if not installations:
            continue

        installation = installations[0]  # Show first installation
        is_enabled = plugin_id in enabled_plugins
        version = installation.get('version', 'unknown')
        scope = installation.get('scope', 'user')
        status = 'enabled' if is_enabled else 'disabled'

        lines.append(f'  • {plugin_id}')
        lines.append(f'    Version: {version}')
        lines.append(f'    Scope: {scope}')
        lines.append(f'    Status: {status}')
        lines.append('')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def list_marketplaces() -> Dict[str, Any]:
    """List configured marketplaces."""
    marketplaces = await load_known_marketplaces_config()

    if not marketplaces:
        return {'type': 'text', 'value': 'No marketplaces configured.\n\nUse /plugins marketplace add <source> to add a marketplace.'}

    lines = ['Configured marketplaces:', '']
    for name, config in marketplaces.items():
        source = config.get('source', {})
        source_display = format_source_for_display(source)
        lines.append(f'  • {name}')
        lines.append(f'    {source_display}')

    return {'type': 'text', 'value': '\n'.join(lines)}


# ============================================================================
# Plugin Operations
# ============================================================================

async def install_plugin(plugin: Optional[str] = None, marketplace: Optional[str] = None) -> Dict[str, Any]:
    """Install a plugin."""
    if not plugin and not marketplace:
        return {'type': 'text', 'value': 'Usage: /plugins install <plugin>[@<marketplace>]'}

    # If marketplace is specified without plugin, treat as marketplace add
    if marketplace and not plugin:
        return await add_marketplace(marketplace)

    # Build plugin identifier
    if marketplace:
        plugin_id = f"{plugin}@{marketplace}"
    else:
        plugin_id = plugin

    result = await install_plugin_op(plugin_id, scope='user')

    if result.success:
        return {'type': 'text', 'value': f'Successfully installed plugin: {result.plugin_id}'}
    else:
        return {'type': 'text', 'value': f'Failed to install plugin: {result.message}'}


async def uninstall_plugin(plugin: Optional[str]) -> Dict[str, Any]:
    """Uninstall a plugin."""
    if not plugin:
        return {'type': 'text', 'value': 'Usage: /plugins uninstall <plugin>'}

    result = await uninstall_plugin_op(plugin, scope='user')

    if result.success:
        return {'type': 'text', 'value': result.message}
    else:
        return {'type': 'text', 'value': f'Failed to uninstall plugin: {result.message}'}


async def enable_plugin(name: Optional[str]) -> Dict[str, Any]:
    """Enable a plugin."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins enable <plugin>'}

    result = await enable_plugin_op(name)

    if result.success:
        return {'type': 'text', 'value': result.message}
    else:
        return {'type': 'text', 'value': f'Failed to enable plugin: {result.message}'}


async def disable_plugin(name: Optional[str]) -> Dict[str, Any]:
    """Disable a plugin."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins disable <plugin>'}

    result = await disable_plugin_op(name)

    if result.success:
        return {'type': 'text', 'value': result.message}
    else:
        return {'type': 'text', 'value': f'Failed to disable plugin: {result.message}'}


async def disable_all_plugins() -> Dict[str, Any]:
    """Disable all plugins."""
    result = await disable_all_plugins_op()

    if result.success:
        return {'type': 'text', 'value': result.message}
    else:
        return {'type': 'text', 'value': f'Failed to disable plugins: {result.message}'}


async def update_plugin(plugin: Optional[str]) -> Dict[str, Any]:
    """Update a plugin."""
    if not plugin:
        return {'type': 'text', 'value': 'Usage: /plugins update <plugin>'}

    result = await update_plugin_op(plugin, scope='user')

    if result.success:
        if result.already_up_to_date:
            return {'type': 'text', 'value': result.message}
        return {'type': 'text', 'value': result.message}
    else:
        return {'type': 'text', 'value': f'Failed to update plugin: {result.message}'}


async def validate_plugin(path: Optional[str]) -> Dict[str, Any]:
    """Validate a plugin."""
    if not path:
        return {'type': 'text', 'value': 'Usage: /plugins validate <path>'}

    plugin_path = Path(path)

    if not plugin_path.exists():
        return {'type': 'text', 'value': f'Path does not exist: {path}'}

    # Look for plugin.json or .claude-plugin/plugin.json
    manifest_paths = [
        plugin_path / '.claude-plugin' / 'plugin.json',
        plugin_path / 'plugin.json',
    ]

    for manifest_path in manifest_paths:
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)

                # Validate required fields
                name = manifest.get('name')
                if not name:
                    return {'type': 'text', 'value': 'Validation failed: plugin name is required'}

                errors = []
                warnings = []

                if ' ' in name:
                    errors.append('Plugin name cannot contain spaces')

                if not manifest.get('version'):
                    warnings.append('Plugin version is not specified')

                if errors:
                    return {'type': 'text', 'value': f"Validation failed:\n  - " + "\n  - ".join(errors)}

                msg = f"Validation passed for: {name}"
                if warnings:
                    msg += f"\nWarnings:\n  - " + "\n  - ".join(warnings)

                return {'type': 'text', 'value': msg}
            except json.JSONDecodeError as e:
                return {'type': 'text', 'value': f'Invalid JSON in manifest: {e}'}

    return {'type': 'text', 'value': 'No plugin manifest found (expected plugin.json or .claude-plugin/plugin.json)'}


# ============================================================================
# Marketplace Operations
# ============================================================================

async def handle_marketplace(action: Optional[str], target: Optional[str]) -> Dict[str, Any]:
    """Handle marketplace subcommands."""
    if action == 'list':
        return await list_marketplaces()

    if action == 'add':
        return await add_marketplace(target)

    if action == 'remove':
        return await remove_marketplace(target)

    if action == 'update':
        if target:
            return await update_marketplace(target)
        return await update_all_marketplaces()

    return {'type': 'text', 'value': '''Usage: /plugins marketplace [command]

Commands:
  marketplace add <source>    Add a marketplace
  marketplace remove <name>   Remove a marketplace
  marketplace list            List configured marketplaces
  marketplace update          Update all marketplaces
  marketplace update <name>   Update specific marketplace
'''}


async def add_marketplace(source: Optional[str]) -> Dict[str, Any]:
    """Add a marketplace."""
    if not source:
        return {'type': 'text', 'value': 'Usage: /plugins marketplace add <source>\n\nSource can be:\n  - https://example.com/marketplace.json (URL)\n  - github:owner/repo (GitHub repo)\n  - npm:package-name (npm package)'}

    # Parse source type
    if source.startswith('http://') or source.startswith('https://'):
        config = {'source': 'url', 'url': source}
    elif source.startswith('github:'):
        repo = source[7:]  # Remove 'github:' prefix
        config = {'source': 'github', 'repo': repo}
    elif source.startswith('npm:'):
        package = source[4:]  # Remove 'npm:' prefix
        config = {'source': 'npm', 'package': package}
    elif source.startswith('git:'):
        url = source[4:]  # Remove 'git:' prefix
        config = {'source': 'git', 'url': url}
    elif source.startswith('dir:') or source.startswith('directory:'):
        path = source.split(':', 1)[1]
        config = {'source': 'directory', 'path': path}
    elif source.startswith('file:'):
        path = source[5:]
        config = {'source': 'file', 'path': path}
    else:
        return {'type': 'text', 'value': f'Unknown source type: {source}'}

    try:
        name, already_materialized, resolved = await add_marketplace_source(config)

        return {'type': 'text', 'value': f'Successfully added marketplace: {name}'}
    except Exception as e:
        return {'type': 'text', 'value': f'Failed to add marketplace: {str(e)}'}


async def remove_marketplace(name: Optional[str]) -> Dict[str, Any]:
    """Remove a marketplace."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins marketplace remove <name>'}

    try:
        await remove_marketplace_source(name)
        return {'type': 'text', 'value': f'Successfully removed marketplace: {name}'}
    except Exception as e:
        return {'type': 'text', 'value': f'Failed to remove marketplace: {str(e)}'}


async def update_marketplace(name: str) -> Dict[str, Any]:
    """Update a specific marketplace."""
    try:
        await refresh_marketplace(name)
        return {'type': 'text', 'value': f'Successfully updated marketplace: {name}'}
    except Exception as e:
        return {'type': 'text', 'value': f'Failed to update marketplace: {str(e)}'}


async def update_all_marketplaces() -> Dict[str, Any]:
    """Update all marketplaces."""
    try:
        await refresh_all_marketplaces()
        config = await load_known_marketplaces_config()
        count = len(config)
        return {'type': 'text', 'value': f'Successfully updated {count} marketplace(s)'}
    except Exception as e:
        return {'type': 'text', 'value': f'Failed to update marketplaces: {str(e)}'}


# ============================================================================
# Command Metadata
# ============================================================================

CONFIG = {
    'type': 'local',
    'name': 'plugins',
    'description': 'Manage plugins and marketplaces',
    'supports_non_interactive': True,
}


call = execute