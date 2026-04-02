"""
Environment variable validation utilities.
"""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnvVarValidationResult:
    """Result of environment variable validation."""
    effective: int
    status: str  # 'valid' | 'capped' | 'invalid'
    message: Optional[str] = None


def validate_bounded_int_env_var(
    name: str,
    value: Optional[str],
    default_value: int,
    upper_limit: int,
) -> EnvVarValidationResult:
    """Validate a bounded integer environment variable.

    Args:
        name: Environment variable name
        value: Environment variable value
        default_value: Default value if invalid
        upper_limit: Upper limit for the value

    Returns:
        EnvVarValidationResult with validation status
    """
    if not value:
        return EnvVarValidationResult(effective=default_value, status="valid")

    try:
        parsed = int(value)
    except ValueError:
        parsed = None

    if parsed is None or parsed <= 0:
        result = EnvVarValidationResult(
            effective=default_value,
            status="invalid",
            message=f'Invalid value "{value}" (using default: {default_value})',
        )
        logger.debug(f"{name} {result.message}")
        return result

    if parsed > upper_limit:
        result = EnvVarValidationResult(
            effective=upper_limit,
            status="capped",
            message=f"Capped from {parsed} to {upper_limit}",
        )
        logger.debug(f"{name} {result.message}")
        return result

    return EnvVarValidationResult(effective=parsed, status="valid")


__all__ = ["EnvVarValidationResult", "validate_bounded_int_env_var"]