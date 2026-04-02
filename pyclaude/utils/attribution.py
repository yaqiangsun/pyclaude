"""
Attribution utilities.

Handles commit and PR attribution text generation.
"""

import os
from typing import Optional, Any, Dict, List
from dataclasses import dataclass

# Product URL constant
PRODUCT_URL = "https://claude.com/claude-code"


@dataclass
class AttributionTexts:
    """Attribution text for commits and PRs."""
    commit: str
    pr: str


# Placeholder - will be implemented with actual dependencies
def _get_public_model_name() -> str:
    """Get public model name placeholder."""
    return "Claude"


def _get_settings() -> Dict[str, Any]:
    """Get settings placeholder."""
    return {}


def get_attribution_texts() -> AttributionTexts:
    """Returns attribution text for commits and PRs based on user settings.

    Returns:
        AttributionTexts with commit and PR attribution strings
    """
    # Check for undercover mode
    if os.environ.get("USER_TYPE") == "ant" and os.environ.get("UNDERCOVER"):
        return AttributionTexts(commit="", pr="")

    # Check for remote session
    if os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID"):
        remote_session_id = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID")
        if remote_session_id:
            ingress_url = os.environ.get("SESSION_INGRESS_URL")
            # Skip for local dev - URLs won't persist
            if ingress_url and "localhost" not in ingress_url:
                session_url = f"{ingress_url}/session/{remote_session_id}"
                return AttributionTexts(commit=session_url, pr=session_url)
        return AttributionTexts(commit="", pr="")

    # Get model name
    model_name = _get_public_model_name()
    default_attribution = f"🤖 Generated with [Claude Code]({PRODUCT_URL})"
    default_commit = f"Co-Authored-By: {model_name} <noreply@anthropic.com>"

    settings = _get_settings()

    # Check for attribution settings
    if settings.get("attribution"):
        return AttributionTexts(
            commit=settings.get("attribution", {}).get("commit", default_commit),
            pr=settings.get("attribution", {}).get("pr", default_attribution),
        )

    # Backward compatibility: check deprecated includeCoAuthoredBy
    if settings.get("includeCoAuthoredBy") is False:
        return AttributionTexts(commit="", pr="")

    return AttributionTexts(commit=default_commit, pr=default_attribution)


def is_terminal_output(content: str) -> bool:
    """Check if message content is terminal output rather than a user prompt.

    Args:
        content: The content to check

    Returns:
        True if content is terminal output
    """
    terminal_output_tags = [
        "terminal_output",
        "bash_history",
        "command",
        "result",
    ]
    for tag in terminal_output_tags:
        if f"<{tag}>" in content:
            return True
    return False


def count_user_prompts_in_messages(messages: List[Dict[str, Any]]) -> int:
    """Count user messages with visible text content.

    Excludes tool_result blocks, terminal output, and empty messages.

    Args:
        messages: List of messages to count

    Returns:
        Number of user prompts
    """
    count = 0
    for message in messages:
        if message.get("type") != "user":
            continue

        content = message.get("message", {}).get("content")
        if not content:
            continue

        has_user_text = False

        if isinstance(content, str):
            if is_terminal_output(content):
                continue
            has_user_text = len(content.strip()) > 0
        elif isinstance(content, list):
            has_user_text = any(
                block.get("type") == "text" and
                isinstance(block.get("text"), str) and
                not is_terminal_output(block.get("text", ""))
                for block in content
                if isinstance(block, dict)
            )

        if has_user_text:
            count += 1

    return count


async def get_enhanced_pr_attribution(
    get_app_state: Any = None,
) -> str:
    """Get enhanced PR attribution text with Claude contribution stats.

    Format: "🤖 Generated with Claude Code (93% 3-shotted by claude-opus-4-5)"

    Args:
        get_app_state: Function to get the current AppState

    Returns:
        Enhanced PR attribution string
    """
    # Check for undercover mode
    if os.environ.get("USER_TYPE") == "ant" and os.environ.get("UNDERCOVER"):
        return ""

    # Check for remote session
    if os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID"):
        remote_session_id = os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID")
        if remote_session_id:
            ingress_url = os.environ.get("SESSION_INGRESS_URL")
            if ingress_url and "localhost" not in ingress_url:
                return f"{ingress_url}/session/{remote_session_id}"
        return ""

    settings = _get_settings()

    # Check for custom attribution
    if settings.get("attribution", {}).get("pr"):
        return settings["attribution"]["pr"]

    if settings.get("includeCoAuthoredBy") is False:
        return ""

    default_attribution = f"🤖 Generated with [Claude Code]({PRODUCT_URL})"
    return default_attribution


__all__ = [
    "AttributionTexts",
    "get_attribution_texts",
    "is_terminal_output",
    "count_user_prompts_in_messages",
    "get_enhanced_pr_attribution",
]