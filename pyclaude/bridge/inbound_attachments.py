"""Inbound attachments handling."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class InboundAttachment:
    """An attachment received via bridge."""
    id: str
    filename: str
    content_type: str
    size: int
    path: Optional[str] = None
    data: Optional[bytes] = None


class InboundAttachmentsHandler:
    """Handler for inbound attachments."""

    def __init__(self):
        self._attachments: Dict[str, InboundAttachment] = {}

    def add_attachment(self, attachment: InboundAttachment) -> None:
        """Add an attachment."""
        self._attachments[attachment.id] = attachment

    def get_attachment(self, attachment_id: str) -> Optional[InboundAttachment]:
        """Get an attachment by ID."""
        return self._attachments.get(attachment_id)

    def list_attachments(self) -> List[InboundAttachment]:
        """List all attachments."""
        return list(self._attachments.values())

    def remove_attachment(self, attachment_id: str) -> bool:
        """Remove an attachment."""
        if attachment_id in self._attachments:
            del self._attachments[attachment_id]
            return True
        return False


# Global handler instance
_attachments_handler = InboundAttachmentsHandler()


def get_attachments_handler() -> InboundAttachmentsHandler:
    """Get the global attachments handler."""
    return _attachments_handler


__all__ = ['InboundAttachment', 'InboundAttachmentsHandler', 'get_attachments_handler']