"""
Billing utilities.
"""

# Mock billing access for testing
_mock_billing_access_override = None


def set_mock_billing_access_override(value: bool | None) -> None:
    """Set mock billing access for testing.

    Args:
        value: True, False, or None to disable mock
    """
    global _mock_billing_access_override
    _mock_billing_access_override = value


def has_console_billing_access() -> bool:
    """Check if user has billing access via console.

    Returns:
        True if user has billing access
    """
    # TODO: Implement with actual auth/config dependencies
    return False


def has_claude_ai_billing_access() -> bool:
    """Check if user has Claude AI (Max/Pro) billing access.

    Returns:
        True if user has Claude AI billing access
    """
    # Check for mock billing access first
    if _mock_billing_access_override is not None:
        return _mock_billing_access_override

    # TODO: Implement with actual auth/config dependencies
    return False


__all__ = [
    "set_mock_billing_access_override",
    "has_console_billing_access",
    "has_claude_ai_billing_access",
]