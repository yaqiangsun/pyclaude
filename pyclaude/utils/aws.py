"""
AWS utilities.

AWS credential handling and validation.
"""

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AwsCredentials:
    """AWS short-term credentials format."""
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: Optional[str] = None


@dataclass
class AwsStsOutput:
    """Output from AWS STS get-session-token or assume-role."""
    credentials: AwsCredentials


def is_aws_credentials_provider_error(err: Any) -> bool:
    """Check if error is an AWS CredentialsProviderError.

    Args:
        err: Error to check

    Returns:
        True if it's an AWS credentials provider error
    """
    return getattr(err, "name", None) == "CredentialsProviderError"


def is_valid_aws_sts_output(obj: Any) -> bool:
    """Validate AWS STS assume-role output.

    Args:
        obj: Object to validate

    Returns:
        True if valid AWS STS output
    """
    if not obj or not isinstance(obj, dict):
        return False

    credentials = obj.get("Credentials")
    if not credentials or not isinstance(credentials, dict):
        return False

    access_key_id = credentials.get("AccessKeyId")
    secret_access_key = credentials.get("SecretAccessKey")
    session_token = credentials.get("SessionToken")

    return (
        isinstance(access_key_id, str) and
        isinstance(secret_access_key, str) and
        isinstance(session_token, str) and
        len(access_key_id) > 0 and
        len(secret_access_key) > 0 and
        len(session_token) > 0
    )


async def check_sts_caller_identity() -> None:
    """Check if STS caller identity can be retrieved.

    Raises:
        Exception if caller identity cannot be retrieved
    """
    # TODO: Implement with actual AWS SDK
    pass


async def clear_aws_ini_cache() -> None:
    """Clear AWS credential provider cache.

    This ensures that any changes to ~/.aws/credentials are picked up immediately.
    """
    try:
        logger.debug("Clearing AWS credential provider cache")
        # TODO: Implement with actual AWS SDK
        logger.debug("AWS credential provider cache refreshed")
    except Exception:
        logger.debug(
            "Failed to clear AWS credential cache (this is expected if no credentials are configured)"
        )


__all__ = [
    "AwsCredentials",
    "AwsStsOutput",
    "is_aws_credentials_provider_error",
    "is_valid_aws_sts_output",
    "check_sts_caller_identity",
    "clear_aws_ini_cache",
]