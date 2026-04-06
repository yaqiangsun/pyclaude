"""Keyboard key constants."""

from typing import Dict


# Key names
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_ENTER = 'enter'
KEY_ESCAPE = 'escape'
KEY_TAB = 'tab'
KEY_BACKSPACE = 'backspace'
KEY_DELETE = 'delete'
KEY_SPACE = ' '

# Modifier keys
MODIFIER_SHIFT = 'shift'
MODIFIER_CTRL = 'ctrl'
MODIFIER_ALT = 'alt'
MODIFIER_META = 'meta'

# Key combinations
KEYBindings: Dict[str, str] = {
    'ctrl+c': 'cancel',
    'ctrl+z': 'undo',
    'ctrl+y': 'redo',
    'ctrl+s': 'save',
    'ctrl+o': 'open',
    'ctrl+p': 'print',
    'ctrl+f': 'find',
    'ctrl+a': 'select_all',
    'ctrl+w': 'close',
    'ctrl+n': 'new',
    'ctrl+t': 'new_tab',
    'ctrl+shift+t': 'restore_tab',
    'ctrl+tab': 'next_tab',
    'ctrl+shift+tab': 'prev_tab',
}


def get_keybinding(action: str) -> str:
    """Get keybinding for an action."""
    return KEYBindings.get(action, '')


def parse_keybinding(keys: str) -> Dict[str, bool]:
    """Parse a keybinding string into modifiers."""
    result = {
        'ctrl': False,
        'shift': False,
        'alt': False,
        'meta': False,
        'key': '',
    }

    parts = keys.lower().split('+')
    for part in parts:
        part = part.strip()
        if part == 'ctrl':
            result['ctrl'] = True
        elif part == 'shift':
            result['shift'] = True
        elif part == 'alt':
            result['alt'] = True
        elif part == 'meta' or part == 'cmd':
            result['meta'] = True
        else:
            result['key'] = part

    return result


__all__ = [
    'KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT', 'KEY_ENTER', 'KEY_ESCAPE',
    'KEY_TAB', 'KEY_BACKSPACE', 'KEY_DELETE', 'KEY_SPACE',
    'MODIFIER_SHIFT', 'MODIFIER_CTRL', 'MODIFIER_ALT', 'MODIFIER_META',
    'KEYBindings', 'get_keybinding', 'parse_keybinding',
]