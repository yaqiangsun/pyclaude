"""Bridge pointer utilities."""

from typing import Optional, Tuple


class BridgePointer:
    """Pointer for navigating bridge messages."""

    def __init__(self, before_id: Optional[str] = None, after_id: Optional[str] = None):
        self.before_id = before_id
        self.after_id = after_id

    def as_dict(self) -> dict:
        """Convert to dictionary."""
        result = {}
        if self.before_id:
            result['before_id'] = self.before_id
        if self.after_id:
            result['after_id'] = self.after_id
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'BridgePointer':
        """Create from dictionary."""
        return cls(
            before_id=data.get('before_id'),
            after_id=data.get('after_id'),
        )


def create_forward_pointer(message_id: str) -> BridgePointer:
    """Create a forward pointer."""
    return BridgePointer(after_id=message_id)


def create_backward_pointer(message_id: str) -> BridgePointer:
    """Create a backward pointer."""
    return BridgePointer(before_id=message_id)


__all__ = ['BridgePointer', 'create_forward_pointer', 'create_backward_pointer']