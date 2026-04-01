"""
Keyboard shortcut utilities.

Special characters that macOS Option+key produces, mapped to their
keybinding equivalents. Used to detect Option+key shortcuts on macOS
terminals that don't have "Option as Meta" enabled.
"""

from typing import Dict


MACOS_OPTION_SPECIAL_CHARS: Dict[str, str] = {
    '†': 'alt+t',  # Option+T -> thinking toggle
    'π': 'alt+p',  # Option+P -> model picker
    'ø': 'alt+o',  # Option+O -> fast mode
}


def is_macos_option_char(char: str) -> bool:
    """Check if character is a macOS Option key special character."""
    return char in MACOS_OPTION_SPECIAL_CHARS