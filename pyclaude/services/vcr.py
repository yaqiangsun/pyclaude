"""
VCR (Video Cassette Recorder) service for recording and replaying API calls.
Used for testing and debugging.
"""
from typing import Optional, Dict, Any, List, Callable
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VCRMode(Enum):
    """VCR recording/replay modes."""
    OFF = "off"
    RECORD = "record"
    PLAYBACK = "playback"
    OVERWRITE = "overwrite"


@dataclass
class VCRRequest:
    """A recorded API request."""
    timestamp: str
    request: Dict[str, Any]
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class VCRCassette:
    """A VCR cassette containing recorded interactions."""
    name: str
    interactions: List[VCRRequest] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VCRService:
    """Service for recording and replaying API calls."""

    _mode: VCRMode = VCRMode.OFF
    _cassette: Optional[VCRCassette] = None
    _cassette_dir: str = ".vcr"

    def __init__(self) -> None:
        # Ensure cassette directory exists
        os.makedirs(self._cassette_dir, exist_ok=True)

    def set_mode(self, mode: VCRMode) -> None:
        """Set the VCR mode."""
        self._mode = mode

    def get_mode(self) -> VCRMode:
        """Get the current VCR mode."""
        return self._mode

    async def load_cassette(self, name: str) -> bool:
        """
        Load a cassette for playback.

        Args:
            name: Name of the cassette file

        Returns:
            True if cassette was loaded successfully
        """
        if self._mode not in (VCRMode.PLAYBACK, VCRMode.OVERWRITE):
            return False

        cassette_path = os.path.join(self._cassette_dir, f"{name}.json")
        if not os.path.exists(cassette_path):
            return False

        try:
            with open(cassette_path, 'r') as f:
                data = json.load(f)
                self._cassette = VCRCassette(
                    name=name,
                    interactions=[
                        VCRRequest(
                            timestamp=i.get('timestamp', ''),
                            request=i.get('request', {}),
                            response=i.get('response'),
                            error=i.get('error'),
                        )
                        for i in data.get('interactions', [])
                    ],
                    metadata=data.get('metadata', {}),
                )
            return True
        except Exception:
            return False

    async def save_cassette(self) -> None:
        """Save the current cassette to disk."""
        if not self._cassette:
            return

        cassette_path = os.path.join(self._cassette_dir, f"{self._cassette.name}.json")
        data = {
            'interactions': [
                {
                    'timestamp': i.timestamp,
                    'request': i.request,
                    'response': i.response,
                    'error': i.error,
                }
                for i in self._cassette.interactions
            ],
            'metadata': self._cassette.metadata,
        }

        with open(cassette_path, 'w') as f:
            json.dump(data, f, indent=2)

    async def record(self, request: Dict[str, Any], response: Optional[Dict[str, Any]] = None) -> None:
        """Record an API interaction."""
        if self._mode not in (VCRMode.RECORD, VCRMode.OVERWRITE):
            return

        if not self._cassette:
            self._cassette = VCRCassette(name="default")

        self._cassette.interactions.append(
            VCRRequest(
                timestamp=datetime.now().isoformat(),
                request=request,
                response=response,
            )
        )

    async def replay(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Replay an API interaction from the cassette.

        Args:
            request: The request to match

        Returns:
            The recorded response, or None if not found
        """
        if self._mode != VCRMode.PLAYBACK or not self._cassette:
            return None

        # Find matching request (simple key-based matching)
        for interaction in self._cassette.interactions:
            if self._requests_match(request, interaction.request):
                return interaction.response

        return None

    def _requests_match(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requests match."""
        # Simple comparison - in full implementation would be more sophisticated
        return req1.get('model') == req2.get('model')

    async def start_recording(self, name: str) -> None:
        """Start recording a new cassette."""
        self._mode = VCRMode.RECORD
        self._cassette = VCRCassette(name=name)

    async def stop_recording(self) -> None:
        """Stop recording and save the cassette."""
        if self._mode == VCRMode.RECORD:
            await self.save_cassette()
        self._mode = VCRMode.OFF


# Singleton instance
_vcr_service: Optional[VCRService] = None


def get_vcr_service() -> VCRService:
    """Get the VCR service singleton."""
    global _vcr_service
    if _vcr_service is None:
        _vcr_service = VCRService()
    return _vcr_service


# Decorator for token count VCR
def with_token_count_vcr(func: Callable) -> Callable:
    """Decorator to wrap token counting with VCR."""
    async def wrapper(*args, **kwargs):
        vcr = get_vcr_service()
        if vcr.get_mode() == VCRMode.PLAYBACK:
            # Try to replay
            request = {'args': str(args), 'kwargs': str(kwargs)}
            result = await vcr.replay(request)
            if result:
                return result

        # Record or normal execution
        result = await func(*args, **kwargs)

        if vcr.get_mode() in (VCRMode.RECORD, VCRMode.OVERWRITE):
            request = {'args': str(args), 'kwargs': str(kwargs)}
            await vcr.record(request, result)

        return result
    return wrapper


__all__ = [
    'VCRService',
    'VCRMode',
    'VCRCassette',
    'VCRRequest',
    'get_vcr_service',
    'with_token_count_vcr',
]