"""
FPS tracker utilities.

Track frames per second for rendering.
"""

from typing import List, Optional
from dataclasses import dataclass
import time


@dataclass
class FPSStats:
    """FPS statistics."""
    current: float
    average: float
    min_fps: float
    max_fps: float


class FPSTracker:
    """Track FPS for rendering."""

    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.frame_times: List[float] = []

    def record_frame(self) -> None:
        """Record a frame timestamp."""
        self.frame_times.append(time.time())
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)

    def get_fps(self) -> float:
        """Get current FPS.

        Returns:
            Current FPS
        """
        if len(self.frame_times) < 2:
            return 0.0

        elapsed = self.frame_times[-1] - self.frame_times[0]
        if elapsed == 0:
            return 0.0

        return (len(self.frame_times) - 1) / elapsed

    def get_stats(self) -> Optional[FPSStats]:
        """Get FPS statistics.

        Returns:
            FPS stats or None
        """
        if len(self.frame_times) < 2:
            return None

        fps_values = []
        for i in range(1, len(self.frame_times)):
            elapsed = self.frame_times[i] - self.frame_times[i - 1]
            if elapsed > 0:
                fps_values.append(1.0 / elapsed)

        if not fps_values:
            return None

        return FPSStats(
            current=fps_values[-1],
            average=sum(fps_values) / len(fps_values),
            min_fps=min(fps_values),
            max_fps=max(fps_values),
        )


# Global tracker
_fps_tracker = FPSTracker()


def get_fps_tracker() -> FPSTracker:
    """Get global FPS tracker."""
    return _fps_tracker


__all__ = [
    "FPSStats",
    "FPSTracker",
    "get_fps_tracker",
]