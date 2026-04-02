"""
Use exit on Ctrl+C/D hook.

Handle ctrl+c and ctrl+d for exiting the application using a time-based
double-press mechanism.
"""

from typing import Callable, Optional
from dataclasses import dataclass

# Import double press handler
from .use_double_press import use_double_press, DOUBLE_PRESS_TIMEOUT_MS


@dataclass
class ExitState:
    """Exit state."""
    pending: bool
    key_name: Optional[str]  # 'Ctrl-C' | 'Ctrl-D' | None


def use_exit_on_ctrl_cd(
    use_keybindings_hook: Callable,
    on_interrupt: Optional[Callable[[], bool]] = None,
    on_exit: Optional[Callable[[], None]] = None,
    is_active: bool = True,
) -> ExitState:
    """Handle ctrl+c and ctrl+d for exiting the application.

    Uses a time-based double-press mechanism:
    - First press: Shows "Press X again to exit" message
    - Second press within timeout: Exits the application

    Args:
        use_keybindings_hook: Hook for registering handlers
        on_interrupt: Optional callback for features to handle interrupt
        on_exit: Optional custom exit handler
        is_active: Whether the keybinding is active

    Returns:
        ExitState with pending state and key name
    """
    exit_state = ExitState(pending=False, key_name=None)

    # Default exit function
    def default_exit():
        import sys
        sys.exit(0)

    exit_fn = on_exit or default_exit

    # Double-press handler for ctrl+c
    def set_ctrl_c_pending(pending: bool):
        exit_state.pending = pending
        exit_state.key_name = 'Ctrl-C' if pending else None

    ctrl_c_handler = use_double_press(
        set_ctrl_c_pending,
        exit_fn,
    )

    # Double-press handler for ctrl+d
    def set_ctrl_d_pending(pending: bool):
        exit_state.pending = pending
        exit_state.key_name = 'Ctrl-D' if pending else None

    ctrl_d_handler = use_double_press(
        set_ctrl_d_pending,
        exit_fn,
    )

    # Handler for interrupt (ctrl+c)
    def handle_interrupt() -> bool:
        if on_interrupt and on_interrupt():
            return True
        ctrl_c_handler()
        return True  # Always mark as handled to continue double-press flow

    # Handler for exit (ctrl+d)
    def handle_exit() -> None:
        ctrl_d_handler()

    handlers = {
        'app:interrupt': handle_interrupt,
        'app:exit': handle_exit,
    }

    use_keybindings_hook(handlers, {'context': 'Global', 'isActive': is_active})

    return exit_state


__all__ = ["ExitState", "use_exit_on_ctrl_cd"]