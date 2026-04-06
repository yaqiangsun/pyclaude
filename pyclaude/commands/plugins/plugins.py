"""Plugins command - manage plugins.

Matches src/commands/plugin/parseArgs.ts command structure:
- install/i
- uninstall
- enable
- disable
- validate
- marketplace (add/remove/update/list)
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


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
    """Load known marketplaces configuration."""
    if KNOWN_MARKETPLACES_FILE.exists():
        try:
            with open(KNOWN_MARKETPLACES_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_known_marketplaces(data: Dict[str, Any]) -> None:
    """Save known marketplaces configuration."""
    get_plugins_dir()
    with open(KNOWN_MARKETPLACES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


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
        return {'type': 'disable', 'plugin': parts[1] if len(parts) > 1 else None}

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

    # Unknown command, show menu
    return {'type': 'menu'}


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


async def execute(args: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the plugins command."""
    parsed = parse_plugin_args(args)

    cmd_type = parsed.get('type', 'menu')

    if cmd_type == 'help':
        return show_help()

    if cmd_type == 'menu':
        return await show_plugin_menu()

    if cmd_type == 'install':
        return await install_plugin(parsed.get('plugin'), parsed.get('marketplace'))

    if cmd_type == 'uninstall':
        return await uninstall_plugin(parsed.get('plugin'))

    if cmd_type == 'enable':
        return await enable_plugin(parsed.get('plugin'))

    if cmd_type == 'disable':
        return await disable_plugin(parsed.get('plugin'))

    if cmd_type == 'validate':
        return await validate_plugin(parsed.get('path'))

    if cmd_type == 'marketplace':
        return await handle_marketplace(parsed.get('action'), parsed.get('target'))

    return show_help()


def show_help() -> Dict[str, Any]:
    """Show help message."""
    return {'type': 'text', 'value': '''Usage: /plugins [command]

Commands:
  install <plugin>           Install a plugin (or /plugins install marketplace_url)
  install <plugin>@<marketplace>  Install plugin from specific marketplace
  uninstall <plugin>         Uninstall a plugin
  enable <plugin>            Enable a plugin
  disable <plugin>           Disable a plugin
  validate [path]            Validate a plugin
  marketplace add <source>   Add a marketplace
  marketplace remove <name>  Remove a marketplace
  marketplace list           List configured marketplaces
  marketplace update         Update all marketplaces

Alias: /plugin, /marketplace
'''}


async def show_plugin_menu() -> Dict[str, Any]:
    """Show the plugin menu (installed plugins)."""
    # First show installed plugins
    plugins_result = await list_installed_plugins()

    # Then show configured marketplaces
    marketplace_result = await list_marketplaces()

    lines = []

    # Add plugins section
    if plugins_result.get('type') == 'text':
        lines.append(plugins_result['value'])
        lines.append('')

    # Add marketplaces section
    if marketplace_result.get('type') == 'text':
        lines.append(marketplace_result['value'])

    return {'type': 'text', 'value': '\n'.join(lines)}


async def list_installed_plugins() -> Dict[str, Any]:
    """List installed plugins from marketplaces cache."""
    cache_dir = get_marketplaces_cache_dir()
    plugins = []

    if cache_dir.exists():
        for marketplace_dir in cache_dir.iterdir():
            if marketplace_dir.is_dir():
                marketplace_name = marketplace_dir.name

                # Look for marketplace.json to get plugin list
                marketplace_json = marketplace_dir / 'marketplace.json'
                if marketplace_json.exists():
                    try:
                        with open(marketplace_json) as f:
                            data = json.load(f)
                            for plugin in data.get('plugins', []):
                                plugins.append({
                                    'name': plugin.get('name', ''),
                                    'version': plugin.get('version', 'unknown'),
                                    'marketplace': marketplace_name,
                                    'description': plugin.get('description', ''),
                                })
                    except Exception:
                        pass
                else:
                    # Fallback: list any .json files in marketplace dir
                    for f in marketplace_dir.glob('*.json'):
                        try:
                            with open(f) as fp:
                                data = json.load(fp)
                                plugins.append({
                                    'name': f.stem,
                                    'version': data.get('version', 'unknown'),
                                    'marketplace': marketplace_name,
                                    'description': data.get('description', ''),
                                })
                        except Exception:
                            pass

    if not plugins:
        return {'type': 'text', 'value': 'No plugins installed.\n\nUse /plugins install <plugin> to install a plugin.'}

    lines = ['Installed plugins:', '']
    for p in plugins:
        lines.append(f'  • {p["name"]} (v{p["version"]}) - {p["marketplace"]}')
        if p.get('description'):
            lines.append(f'    {p["description"]}')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def list_marketplaces() -> Dict[str, Any]:
    """List configured marketplaces."""
    marketplaces = load_known_marketplaces()

    if not marketplaces:
        return {'type': 'text', 'value': 'No marketplaces configured.\n\nUse /plugins marketplace add <source> to add a marketplace.'}

    lines = ['Configured marketplaces:', '']
    for name, config in marketplaces.items():
        source = config.get('source', {})
        source_display = format_source_for_display(source)
        lines.append(f'  • {name}')
        lines.append(f'    {source_display}')

    return {'type': 'text', 'value': '\n'.join(lines)}


async def install_plugin(plugin: Optional[str] = None, marketplace: Optional[str] = None) -> Dict[str, Any]:
    """Install a plugin."""
    if not plugin and not marketplace:
        return {'type': 'text', 'value': 'Usage: /plugins install <plugin>[@<marketplace>]'}

    if marketplace:
        return {'type': 'text', 'value': f'Installing {plugin or "marketplace"} from {marketplace}... (not implemented)'}

    if plugin:
        return {'type': 'text', 'value': f'Installing plugin: {plugin}... (not implemented)'}

    return show_help()


async def uninstall_plugin(plugin: Optional[str]) -> Dict[str, Any]:
    """Uninstall a plugin."""
    if not plugin:
        return {'type': 'text', 'value': 'Usage: /plugins uninstall <plugin>'}

    # TODO: Implement actual uninstall
    return {'type': 'text', 'value': f'Uninstalling plugin: {plugin}... (not implemented)'}


async def enable_plugin(name: Optional[str]) -> Dict[str, Any]:
    """Enable a plugin."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins enable <plugin>'}

    # TODO: Implement actual enable
    return {'type': 'text', 'value': f'Enabling plugin: {name}... (not implemented)'}


async def disable_plugin(name: Optional[str]) -> Dict[str, Any]:
    """Disable a plugin."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins disable <plugin>'}

    # TODO: Implement actual disable
    return {'type': 'text', 'value': f'Disabling plugin: {name}... (not implemented)'}


async def validate_plugin(path: Optional[str]) -> Dict[str, Any]:
    """Validate a plugin."""
    if not path:
        return {'type': 'text', 'value': 'Usage: /plugins validate <path>'}

    return {'type': 'text', 'value': f'Validating plugin at {path}... (not implemented)'}


async def handle_marketplace(action: Optional[str], target: Optional[str]) -> Dict[str, Any]:
    """Handle marketplace subcommands."""
    if action == 'list':
        return await list_marketplaces()

    if action == 'add':
        return await add_marketplace(target)

    if action == 'remove':
        return await remove_marketplace(target)

    if action == 'update':
        return await update_marketplaces()

    return {'type': 'text', 'value': '''Usage: /plugins marketplace [command]

Commands:
  marketplace add <source>    Add a marketplace
  marketplace remove <name>   Remove a marketplace
  marketplace list            List configured marketplaces
  marketplace update          Update all marketplaces
'''}


async def add_marketplace(source: Optional[str]) -> Dict[str, Any]:
    """Add a marketplace."""
    if not source:
        return {'type': 'text', 'value': 'Usage: /plugins marketplace add <source>\n\nSource can be:\n  - https://example.com/marketplace.json (URL)\n  - github:owner/repo (GitHub repo)\n  - npm:package-name (npm package)'}

    # Parse source type
    if source.startswith('http://') or source.startswith('https://'):
        config = {'source': {'source': 'url', 'url': source}}
    elif source.startswith('github:'):
        repo = source[7:]  # Remove 'github:' prefix
        config = {'source': {'source': 'github', 'repo': repo}}
    elif source.startswith('npm:'):
        package = source[4:]  # Remove 'npm:' prefix
        config = {'source': {'source': 'npm', 'package': package}}
    elif source.startswith('git:'):
        url = source[4:]  # Remove 'git:' prefix
        config = {'source': {'source': 'git', 'url': url}}
    elif source.startswith('dir:') or source.startswith('directory:'):
        path = source.split(':', 1)[1]
        config = {'source': {'source': 'directory', 'path': path}}
    elif source.startswith('file:'):
        path = source[5:]
        config = {'source': {'source': 'file', 'path': path}}
    else:
        return {'type': 'text', 'value': f'Unknown source type: {source}'}

    # Generate marketplace name from source
    if config['source']['source'] == 'github':
        name = config['source']['repo'].split('/')[-1]
    elif config['source']['source'] == 'url':
        from urllib.parse import urlparse
        parsed = urlparse(config['source']['url'])
        name = parsed.netloc.replace('.', '_')
    else:
        name = config['source'].get('package', config['source'].get('path', 'unknown'))

    marketplaces = load_known_marketplaces()
    marketplaces[name] = config
    save_known_marketplaces(marketplaces)

    return {'type': 'text', 'value': f'Added marketplace: {name}\n  Source: {format_source_for_display(config["source"])}'}


async def remove_marketplace(name: Optional[str]) -> Dict[str, Any]:
    """Remove a marketplace."""
    if not name:
        return {'type': 'text', 'value': 'Usage: /plugins marketplace remove <name>'}

    marketplaces = load_known_marketplaces()

    if name not in marketplaces:
        return {'type': 'text', 'value': f'Marketplace "{name}" not found.'}

    del marketplaces[name]
    save_known_marketplaces(marketplaces)

    return {'type': 'text', 'value': f'Removed marketplace: {name}'}


async def update_marketplaces() -> Dict[str, Any]:
    """Update all marketplaces."""
    marketplaces = load_known_marketplaces()

    if not marketplaces:
        return {'type': 'text', 'value': 'No marketplaces to update.'}

    # TODO: Implement actual marketplace update
    return {'type': 'text', 'value': f'Updating {len(marketplaces)} marketplace(s)... (not implemented)'}


# Command metadata
CONFIG = {
    'type': 'local',
    'name': 'plugins',
    'description': 'Manage plugins and marketplaces',
    'supports_non_interactive': True,
}


call = execute