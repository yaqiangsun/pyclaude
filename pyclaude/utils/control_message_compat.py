"""
Control message compatibility utilities.

Normalize camelCase requestId → snake_case request_id on incoming
control messages (control_request, control_response).

Older iOS app builds send requestId due to a missing Swift CodingKeys
mapping. Without this shim, isSDKControlRequest in replBridge.ts rejects
the message (it checks 'request_id' in value), and structuredIO.ts reads
message.response.request_id as undefined — both silently drop the message.

If both request_id and requestId are present, snake_case wins.
"""

from typing import Any, Dict, Optional


def normalize_control_message_keys(obj: Any) -> Any:
    """Normalize camelCase requestId to snake_case request_id.

    Mutates the object in place.

    Args:
        obj: The object to normalize

    Returns:
        The normalized object
    """
    if obj is None or not isinstance(obj, dict):
        return obj

    # Handle top-level requestId
    if "requestId" in obj and "request_id" not in obj:
        obj["request_id"] = obj.pop("requestId")

    # Handle nested response.requestId
    response = obj.get("response")
    if response is not None and isinstance(response, dict):
        if "requestId" in response and "request_id" not in response:
            response["request_id"] = response.pop("requestId")

    return obj


__all__ = ["normalize_control_message_keys"]