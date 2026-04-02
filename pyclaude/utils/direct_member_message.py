"""
Direct member message utilities.

Parse @agent-name message syntax for direct team member messaging.
"""

import re
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DirectMessageResult:
    """Result of sending a direct message."""
    success: bool
    error: Optional[str] = None
    recipient_name: Optional[str] = None


def parse_direct_member_message(input_str: str) -> Optional[Dict[str, str]]:
    """Parse @agent-name message syntax.

    Args:
        input_str: The input string to parse

    Returns:
        Dict with recipientName and message, or None if invalid
    """
    match = re.match(r"^@([\w-]+)\s+(.+)$", input_str, re.DOTALL)
    if not match:
        return None

    recipient_name = match.group(1)
    message = match.group(2)

    if not recipient_name or not message:
        return None

    trimmed_message = message.strip()
    if not trimmed_message:
        return None

    return {"recipientName": recipient_name, "message": trimmed_message}


# Stub type for team context
class TeamContext:
    """Team context placeholder."""
    teammates: Dict[str, Any] = {}
    team_name: str = ""


async def send_direct_member_message(
    recipient_name: str,
    message: str,
    team_context: Optional[TeamContext] = None,
    write_to_mailbox: Optional[Any] = None,
) -> DirectMessageResult:
    """Send a direct message to a team member, bypassing the model.

    Args:
        recipient_name: Name of the recipient
        message: Message to send
        team_context: Team context
        write_to_mailbox: Function to write to mailbox

    Returns:
        DirectMessageResult
    """
    if not team_context or not write_to_mailbox:
        return DirectMessageResult(success=False, error="no_team_context")

    # Find team member by name
    member = None
    for teammate in team_context.teammates.values():
        if teammate.get("name") == recipient_name:
            member = teammate
            break

    if not member:
        return DirectMessageResult(
            success=False,
            error="unknown_recipient",
            recipient_name=recipient_name,
        )

    await write_to_mailbox(
        recipient_name,
        {
            "from": "user",
            "text": message,
            "timestamp": datetime.now().isoformat(),
        },
        team_context.team_name,
    )

    return DirectMessageResult(success=True, recipient_name=recipient_name)


__all__ = [
    "DirectMessageResult",
    "parse_direct_member_message",
    "send_direct_member_message",
]