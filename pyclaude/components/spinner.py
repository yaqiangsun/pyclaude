"""Spinner component."""
import time
from typing import Optional


class Spinner:
    """Terminal spinner component.

    Displays an animated spinner in the terminal.
    """

    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def __init__(self, text: str = "", interval: float = 0.1):
        self.text = text
        self.interval = interval
        self._frame = 0
        self._last_update = 0.0

    def update(self, text: Optional[str] = None) -> str:
        """Update spinner and return current frame."""
        if text is not None:
            self.text = text

        now = time.time()
        if now - self._last_update >= self.interval:
            self._frame = (self._frame + 1) % len(self.FRAMES)
            self._last_update = now

        return f"{self.FRAMES[self._frame]} {self.text}"

    def __str__(self) -> str:
        return self.update()


__all__ = ['Spinner']