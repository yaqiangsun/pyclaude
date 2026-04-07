"""Load User Bindings."""
import json
import os
from pathlib import Path
from typing import Any, Optional

from pyclaude.utils.env_utils import get_claude_config_home_dir


def is_keybinding_customization_enabled() -> bool:
    """Check if keybinding customization is enabled.

    Currently returns False by default (feature gated).
    """
    # Check for environment variable to enable
    return os.environ.get('CLAUDE_KEYBINDING_CUSTOMIZATION', '').lower() in ('1', 'true', 'yes')


def get_keybindings_path() -> str:
    """Get the path to the user keybindings file."""
    return os.path.join(get_claude_config_home_dir(), 'keybindings.json')


def is_keybinding_block(obj: dict) -> bool:
    """Type guard to check if an object is a valid KeybindingBlock."""
    if not isinstance(obj, dict):
        return False
    return 'context' in obj and 'bindings' in obj and isinstance(obj['bindings'], dict)


def is_keybinding_block_array(arr: list) -> bool:
    """Check if a list contains only valid KeybindingBlocks."""
    if not isinstance(arr, list):
        return False
    return all(is_keybinding_block(item) for item in arr)


def check_duplicate_keys_in_json(content: str) -> list[dict]:
    """Check for duplicate keys in JSON (JSON.parse silently drops earlier values)."""
    warnings = []
    seen_keys = {}
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Simple regex to find key: value patterns
        import re
        matches = re.findall(r'"([^"]+)"\s*:', line)
        for key in matches:
            if key in seen_keys:
                warnings.append({
                    'type': 'duplicate_key',
                    'severity': 'warn',
                    'message': f'Duplicate key "{key}" found',
                    'line': line_num,
                })
            else:
                seen_keys[key] = line_num

    return warnings


def parse_binding(key: str, value: Any) -> dict:
    """Parse a keybinding value."""
    if isinstance(value, str):
        return {'key': key, 'command': value, 'when': None}
    if isinstance(value, dict):
        return {
            'key': key,
            'command': value.get('command'),
            'when': value.get('when'),
        }
    return {'key': key, 'command': str(value), 'when': None}


def parse_bindings(blocks: list[dict]) -> list[dict]:
    """Parse keybinding blocks into a flat list of parsed bindings."""
    results = []

    for block in blocks:
        context = block.get('context', 'global')
        bindings = block.get('bindings', {})

        for key, value in bindings.items():
            parsed = parse_binding(key, value)
            parsed['context'] = context
            results.append(parsed)

    return results


def validate_bindings(blocks: list[dict], all_bindings: list[dict]) -> list[dict]:
    """Validate keybinding blocks."""
    warnings = []

    # Check for duplicate key+context combinations
    seen = {}
    for binding in all_bindings:
        key = binding.get('key', '')
        context = binding.get('context', 'global')
        combo = f'{context}:{key}'

        if combo in seen:
            warnings.append({
                'type': 'duplicate_binding',
                'severity': 'warn',
                'message': f'Duplicate binding for key "{key}" in context "{context}"',
            })
        else:
            seen[combo] = True

    return warnings


class KeybindingsLoadResult:
    """Result of loading keybindings, including any validation warnings."""

    def __init__(self, bindings: list[dict], warnings: list[dict]):
        self.bindings = bindings
        self.warnings = warnings


# Cache for bindings
_cached_bindings: Optional[list[dict]] = None
_cached_warnings: list[dict] = []


def get_default_bindings() -> list[dict]:
    """Get default keybindings."""
    return [
        {'key': 'Enter', 'command': 'submit', 'context': 'global'},
        {'key': 'Shift+Enter', 'command': 'newline', 'context': 'global'},
        {'key': 'ArrowUp', 'command': 'history-prev', 'context': 'global'},
        {'key': 'ArrowDown', 'command': 'history-next', 'context': 'global'},
        {'key': 'Ctrl+C', 'command': 'cancel', 'context': 'global'},
        {'key': 'Ctrl+L', 'command': 'clear', 'context': 'global'},
    ]


async def load_keybindings() -> KeybindingsLoadResult:
    """Load and parse keybindings from user config file.

    Returns merged default + user bindings along with validation warnings.
    """
    global _cached_bindings, _cached_warnings

    default_bindings = get_defaultParsedBindings()

    # Skip user config loading if disabled
    if not is_keybinding_customization_enabled():
        return KeybindingsLoadResult(default_bindings, [])

    user_path = get_keybindings_path()

    if not os.path.exists(user_path):
        return KeybindingsLoadResult(default_bindings, [])

    try:
        with open(user_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parsed = json.loads(content)

        # Extract bindings array from object wrapper format: { "bindings": [...] }
        if isinstance(parsed, dict) and 'bindings' in parsed:
            user_blocks = parsed['bindings']
        else:
            return KeybindingsLoadResult(
                default_bindings,
                [{
                    'type': 'parse_error',
                    'severity': 'error',
                    'message': 'keybindings.json must have a "bindings" array',
                    'suggestion': 'Use format: { "bindings": [ ... ] }',
                }]
            )

        # Validate structure
        if not is_keybinding_block_array(user_blocks):
            return KeybindingsLoadResult(
                default_bindings,
                [{
                    'type': 'parse_error',
                    'severity': 'error',
                    'message': '"bindings" must be an array of valid keybinding blocks',
                    'suggestion': 'Each block must have "context" (string) and "bindings" (object)',
                }]
            )

        user_parsed = parse_bindings(user_blocks)

        # User bindings come after defaults, so they override
        merged_bindings = [*default_bindings, *user_parsed]

        # Run validation
        duplicate_warnings = check_duplicate_keys_in_json(content)
        validation_warnings = validate_bindings(user_blocks, merged_bindings)

        all_warnings = [*duplicate_warnings, *validation_warnings]

        # Cache results
        _cached_bindings = merged_bindings
        _cached_warnings = all_warnings

        return KeybindingsLoadResult(merged_bindings, all_warnings)

    except json.JSONDecodeError as e:
        return KeybindingsLoadResult(
            default_bindings,
            [{
                'type': 'parse_error',
                'severity': 'error',
                'message': f'Failed to parse keybindings.json: {str(e)}',
            }]
        )
    except OSError:
        return KeybindingsLoadResult(default_bindings, [])


def get_defaultParsedBindings() -> list[dict]:
    """Parse default bindings."""
    return parse_bindings([
        {
            'context': 'global',
            'bindings': {
                'Enter': 'submit',
                'Shift+Enter': 'newline',
                'ArrowUp': 'history-prev',
                'ArrowDown': 'history-next',
                'Ctrl+C': 'cancel',
                'Ctrl+L': 'clear',
            }
        }
    ])


def load_keybindings_sync() -> list[dict]:
    """Load keybindings synchronously (for initial render).

    Uses cached value if available.
    """
    global _cached_bindings

    if _cached_bindings is not None:
        return _cached_bindings

    result = load_keybindings_sync_with_warnings()
    return result.bindings


def load_keybindings_sync_with_warnings() -> KeybindingsLoadResult:
    """Load keybindings synchronously with validation warnings.

    Uses cached values if available.
    """
    global _cached_bindings, _cached_warnings

    if _cached_bindings is not None:
        return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

    default_bindings = get_defaultParsedBindings()

    # Skip user config loading if disabled
    if not is_keybinding_customization_enabled():
        _cached_bindings = default_bindings
        _cached_warnings = []
        return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

    user_path = get_keybindings_path()

    if not os.path.exists(user_path):
        _cached_bindings = default_bindings
        _cached_warnings = []
        return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

    try:
        with open(user_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parsed = json.loads(content)

        # Extract bindings array
        if isinstance(parsed, dict) and 'bindings' in parsed:
            user_blocks = parsed['bindings']
        else:
            _cached_bindings = default_bindings
            _cached_warnings = [{
                'type': 'parse_error',
                'severity': 'error',
                'message': 'keybindings.json must have a "bindings" array',
                'suggestion': 'Use format: { "bindings": [ ... ] }',
            }]
            return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

        # Validate structure
        if not is_keybinding_block_array(user_blocks):
            _cached_bindings = default_bindings
            _cached_warnings = [{
                'type': 'parse_error',
                'severity': 'error',
                'message': '"bindings" must be an array',
            }]
            return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

        user_parsed = parse_bindings(user_blocks)
        _cached_bindings = [*default_bindings, *user_parsed]

        # Validation
        duplicate_warnings = check_duplicate_keys_in_json(content)
        _cached_warnings = [
            *duplicate_warnings,
            *validate_bindings(user_blocks, _cached_bindings),
        ]

        return KeybindingsLoadResult(_cached_bindings, _cached_warnings)

    except (json.JSONDecodeError, OSError):
        _cached_bindings = default_bindings
        _cached_warnings = []
        return KeybindingsLoadResult(_cached_bindings, _cached_warnings)


def get_cached_keybinding_warnings() -> list[dict]:
    """Get the cached keybinding warnings.

    Returns empty list if no warnings or bindings haven't been loaded yet.
    """
    return _cached_warnings


def reset_keybinding_loader_for_testing() -> None:
    """Reset internal state for testing."""
    global _cached_bindings, _cached_warnings
    _cached_bindings = None
    _cached_warnings = []


def load_user_bindings() -> dict[str, Any]:
    """Load user-defined keybindings from config.

    Returns a dictionary with bindings and warnings.
    """
    result = load_keybindings_sync_with_warnings()
    return {
        'bindings': result.bindings,
        'warnings': result.warnings,
    }


__all__ = [
    'is_keybinding_customization_enabled',
    'get_keybindings_path',
    'load_user_bindings',
    'load_keybindings',
    'load_keybindings_sync',
    'load_keybindings_sync_with_warnings',
    'get_cached_keybinding_warnings',
    'reset_keybinding_loader_for_testing',
    'KeybindingsLoadResult',
]