"""
Attach error log and analytics sinks, draining any events queued before
attachment.

Leaf module — kept out of setup.ts to avoid the setup → commands → bridge
→ setup import cycle.
"""


def init_sinks() -> None:
    """Initialize error log and analytics sinks."""
    # Placeholder - would initialize actual sinks
    pass