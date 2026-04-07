"""
Voice keyterms - Keyword detection for voice commands.
"""
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass


@dataclass
class Keyterm:
    """A keyword/phrase for voice detection."""
    phrase: str
    confidence: float = 0.8
    action: Optional[str] = None


# Default keyterms for Claude Code
DEFAULT_KEYTERMS = [
    Keyterm(phrase="hey Claude", confidence=0.9, action="wake"),
    Keyterm(phrase="stop", confidence=0.8, action="stop"),
    Keyterm(phrase="pause", confidence=0.8, action="pause"),
    Keyterm(phrase="resume", confidence=0.8, action="resume"),
    Keyterm(phrase="help", confidence=0.7, action="help"),
]


class VoiceKeyterms:
    """Voice keyword detection."""

    def __init__(self, keyterms: Optional[List[Keyterm]] = None):
        self.keyterms = keyterms or DEFAULT_KEYTERMS
        self._phrase_set: Set[str] = {kt.phrase.lower() for kt in self.keyterms}

    def add_keyterm(self, keyterm: Keyterm) -> None:
        """Add a new keyterm."""
        self.keyterms.append(keyterm)
        self._phrase_set.add(keyterm.phrase.lower())

    def remove_keyterm(self, phrase: str) -> None:
        """Remove a keyterm by phrase."""
        self.keyterms = [kt for kt in self.keyterms if kt.phrase.lower() != phrase.lower()]
        self._phrase_set.discard(phrase.lower())

    def detect(self, text: str) -> Optional[Keyterm]:
        """
        Detect keyterms in text.

        Args:
            text: Input text to check

        Returns:
            Detected keyterm or None
        """
        text_lower = text.lower()
        for keyterm in self.keyterms:
            if keyterm.phrase.lower() in text_lower:
                return keyterm
        return None

    def get_action(self, text: str) -> Optional[str]:
        """Get the action for detected keyterm."""
        keyterm = self.detect(text)
        return keyterm.action if keyterm else None


# Singleton instance
_voice_keyterms: Optional[VoiceKeyterms] = None


def get_voice_keyterms() -> VoiceKeyterms:
    """Get the voice keyterms singleton."""
    global _voice_keyterms
    if _voice_keyterms is None:
        _voice_keyterms = VoiceKeyterms()
    return _voice_keyterms


__all__ = ['Keyterm', 'VoiceKeyterms', 'DEFAULT_KEYTERMS', 'get_voice_keyterms']