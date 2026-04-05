"""Cross-platform terminal clearing with scrollback support."""
import os


# ANSI escape codes
CURSOR_HOME = '\x1b[H'
CSI = '\x1b['
ERASE_SCREEN = '\x1b[2J'
ERASE_SCROLLBACK = '\x1b[3J'


def _csi(params: str, final: str) -> str:
    """Generate CSI escape sequence."""
    return f'{CSI}{params}{final}'


# HVP (Horizontal Vertical Position) - legacy Windows cursor home
CURSOR_HOME_WINDOWS = _csi('0', 'f')


def _is_windows_terminal() -> bool:
    """Check if running in Windows Terminal."""
    return os.name == 'nt' and bool(os.environ.get('WT_SESSION'))


def _is_mintty() -> bool:
    """Check if running in mintty."""
    if os.environ.get('TERM_PROGRAM') == 'mintty':
        return True
    # GitBash/MSYS2/MINGW use mintty
    if os.name == 'nt' and os.environ.get('MSYSTEM'):
        return True
    return False


def _is_modern_windows_terminal() -> bool:
    """Check if terminal supports modern escape sequences."""
    # Windows Terminal
    if _is_windows_terminal():
        return True

    # VS Code integrated terminal on Windows
    if (os.name == 'nt' and
        os.environ.get('TERM_PROGRAM') == 'vscode' and
        os.environ.get('TERM_PROGRAM_VERSION')):
        return True

    # mintty
    if _is_mintty():
        return True

    return False


def get_clear_terminal_sequence() -> str:
    """Get ANSI escape sequence to clear terminal including scrollback."""
    if os.name == 'nt':
        if _is_modern_windows_terminal():
            return ERASE_SCREEN + ERASE_SCROLLBACK + CURSOR_HOME
        else:
            # Legacy Windows console
            return ERASE_SCREEN + CURSOR_HOME_WINDOWS
    return ERASE_SCREEN + ERASE_SCROLLBACK + CURSOR_HOME


# Pre-computed clear sequence
clear_terminal = get_clear_terminal_sequence()


__all__ = ['clear_terminal', 'get_clear_terminal_sequence']