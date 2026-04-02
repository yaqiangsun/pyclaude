"""
Hooks module - React hooks adaptation.

Python version uses callback/state pattern instead of React hooks.
"""

from .use_blink import BlinkState, use_blink
from .use_after_first_render import use_after_first_render
from .use_api_key_verification import use_api_key_verification
from .use_cancel_request import use_cancel_request
from .use_timeout import TimeoutState, use_timeout
from .use_terminal_size import use_terminal_size
from .use_command_queue import use_command_queue
from .use_settings import use_settings
from .use_elapsed_time import use_elapsed_time, format_duration
from .use_input_buffer import use_input_buffer
from .use_clipboard_image_hint import check_clipboard_and_notify
from .use_diff_data import DiffFile, DiffData, use_diff_data

__all__ = [
    "BlinkState",
    "use_blink",
    "use_after_first_render",
    "use_api_key_verification",
    "use_cancel_request",
    "TimeoutState",
    "use_timeout",
    "use_terminal_size",
    "use_command_queue",
    "use_settings",
    "use_elapsed_time",
    "format_duration",
    "use_input_buffer",
    "check_clipboard_and_notify",
    "DiffFile",
    "DiffData",
    "use_diff_data",
]