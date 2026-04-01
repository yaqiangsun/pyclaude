"""
Whether inference-config commands (/model, /fast, /effort) should execute
immediately (during a running query) rather than waiting for the current
turn to finish.

Always enabled for ants; gated by experiment for external users.
"""

import os


def should_inference_config_command_be_immediate() -> bool:
    """Check if inference config commands should be immediate."""
    if os.environ.get('USER_TYPE') == 'ant':
        return True
    # Feature flag check would go here - return False for now
    return False