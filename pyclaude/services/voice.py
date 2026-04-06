"""
Voice service for handling voice input/output.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol


class VoiceInput(Protocol):
    """Protocol for voice input."""
    def start_listening(self) -> None: ...
    def stop_listening(self) -> None: ...


class VoiceOutput(Protocol):
    """Protocol for voice output."""
    def speak(self, text: str) -> None: ...
    def stop_speaking(self) -> None: ...


@dataclass
class VoiceConfig:
    """Configuration for voice features."""
    enabled: bool = False
    input_language: str = "en-US"
    output_voice: str = "default"
    input_device: Optional[str] = None
    output_device: Optional[str] = None


class VoiceService:
    """Service for handling voice features."""

    _instance: Optional['VoiceService'] = None
    _config: VoiceConfig = VoiceConfig()
    _input: Optional[VoiceInput] = None
    _output: Optional[VoiceOutput] = None
    _is_listening: bool = False

    def __new__(cls) -> 'VoiceService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'VoiceService':
        """Get the singleton instance."""
        return cls()

    def configure(self, config: VoiceConfig) -> None:
        """Configure the voice service."""
        self._config = config

    def is_enabled(self) -> bool:
        """Check if voice is enabled."""
        return self._config.enabled

    async def start_listening(self) -> None:
        """Start voice input listening."""
        if not self.is_enabled():
            return
        if self._input:
            self._input.start_listening()
            self._is_listening = True

    async def stop_listening(self) -> None:
        """Stop voice input listening."""
        if self._input:
            self._input.stop_listening()
            self._is_listening = False

    async def speak(self, text: str) -> None:
        """Speak the given text."""
        if not self.is_enabled() or not self._output:
            return
        self._output.speak(text)

    async def stop_speaking(self) -> None:
        """Stop speaking."""
        if self._output:
            self._output.stop_speaking()

    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._is_listening


# Singleton instance
voice_service = VoiceService.get_instance()


__all__ = ['VoiceService', 'VoiceConfig', 'voice_service']