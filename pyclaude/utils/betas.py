"""
Beta feature utilities.

Manages beta feature flags and headers.
"""

import os
from typing import List, Dict, Optional, Any
from functools import lru_cache

# Beta headers (from constants)
BEDROCK_EXTRA_PARAMS_HEADERS = "bedrock-extra-params"
CLAUDE_CODE_20250219_BETA_HEADER = "claude-code-20250219"
CLI_INTERNAL_BETA_HEADER = "cli-internal"
CONTEXT_1M_BETA_HEADER = "context-1m"
CONTEXT_MANAGEMENT_BETA_HEADER = "context-management"
INTERLEAVED_THINKING_BETA_HEADER = "interleaved-thinking"
PROMPT_CACHING_SCOPE_BETA_HEADER = "prompt-caching-scope"
REDACT_THINKING_BETA_HEADER = "redact-thinking"
STRUCTURED_OUTPUTS_BETA_HEADER = "structured-outputs"
SUMMARIZE_CONNECTOR_TEXT_BETA_HEADER = "summarize-connector-text"
TOKEN_EFFICIENT_TOOLS_BETA_HEADER = "token-efficient-tools"
TOOL_SEARCH_BETA_HEADER_1P = "tool-search-1p"
TOOL_SEARCH_BETA_HEADER_3P = "tool-search-3p"
WEB_SEARCH_BETA_HEADER = "web-search"


# SDK-provided betas that are allowed for API key users
ALLOWED_SDK_BETAS = [CONTEXT_1M_BETA_HEADER]


def partition_betas_by_allowlist(betas: List[str]) -> Dict[str, List[str]]:
    """Filter betas to only include those in the allowlist.

    Args:
        betas: List of beta headers

    Returns:
        Dict with allowed and disallowed betas
    """
    allowed = []
    disallowed = []
    for beta in betas:
        if beta in ALLOWED_SDK_BETAS:
            allowed.append(beta)
        else:
            disallowed.append(beta)
    return {"allowed": allowed, "disallowed": disallowed}


def is_env_truthy(env_var: Optional[str]) -> bool:
    """Check if environment variable is truthy."""
    if not env_var:
        return False
    return env_var.lower() in ("1", "true", "yes", "on")


@lru_cache(maxsize=1)
def get_enabled_betas() -> List[str]:
    """Get list of enabled beta features.

    Returns:
        List of enabled beta headers
    """
    betas: List[str] = []

    # Add beta headers based on environment and settings
    if os.environ.get("CLAUDE_BETA_CONTEXT_1M"):
        betas.append(CONTEXT_1M_BETA_HEADER)

    if os.environ.get("CLAUDE_BETA_PROMPT_CACHING"):
        betas.append(PROMPT_CACHING_SCOPE_BETA_HEADER)

    if os.environ.get("CLAUDE_BETA_WEB_SEARCH"):
        betas.append(WEB_SEARCH_BETA_HEADER)

    return betas


def get_beta_headers() -> Dict[str, str]:
    """Get beta headers for API requests.

    Returns:
        Dict of beta header names to values
    """
    enabled = get_enabled_betas()
    headers = {}
    for beta in enabled:
        headers[f"x-beta-{beta}"] = "1"
    return headers


__all__ = [
    "ALLOWED_SDK_BETAS",
    "partition_betas_by_allowlist",
    "get_enabled_betas",
    "get_beta_headers",
    # Export beta header constants
    "BEDROCK_EXTRA_PARAMS_HEADERS",
    "CLAUDE_CODE_20250219_BETA_HEADER",
    "CLI_INTERNAL_BETA_HEADER",
    "CONTEXT_1M_BETA_HEADER",
    "CONTEXT_MANAGEMENT_BETA_HEADER",
    "INTERLEAVED_THINKING_BETA_HEADER",
    "PROMPT_CACHING_SCOPE_BETA_HEADER",
    "REDACT_THINKING_BETA_HEADER",
    "STRUCTURED_OUTPUTS_BETA_HEADER",
    "SUMMARIZE_CONNECTOR_TEXT_BETA_HEADER",
    "TOKEN_EFFICIENT_TOOLS_BETA_HEADER",
    "TOOL_SEARCH_BETA_HEADER_1P",
    "TOOL_SEARCH_BETA_HEADER_3P",
    "WEB_SEARCH_BETA_HEADER",
]