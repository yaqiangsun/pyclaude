"""Stats context for FPS metrics."""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FPSMetrics:
    """FPS metrics."""
    fps: float = 0
    frame_count: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    min_fps: float = 0
    max_fps: float = 0


class StatsContext:
    """Context for tracking stats."""

    def __init__(self):
        self._fps_metrics = FPSMetrics()
        self._custom_metrics: Dict[str, Any] = {}

    def update_fps(self, fps: float) -> None:
        """Update FPS metrics."""
        self._fps_metrics.fps = fps
        self._fps_metrics.frame_count += 1
        self._fps_metrics.last_update = datetime.now()

        if self._fps_metrics.min_fps == 0 or fps < self._fps_metrics.min_fps:
            self._fps_metrics.min_fps = fps
        if fps > self._fps_metrics.max_fps:
            self._fps_metrics.max_fps = fps

    def get_fps_metrics(self) -> FPSMetrics:
        """Get FPS metrics."""
        return self._fps_metrics

    def set_custom_metric(self, key: str, value: Any) -> None:
        """Set a custom metric."""
        self._custom_metrics[key] = value

    def get_custom_metric(self, key: str) -> Any:
        """Get a custom metric."""
        return self._custom_metrics.get(key)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            'fps': self._fps_metrics.fps,
            'frame_count': self._fps_metrics.frame_count,
            'min_fps': self._fps_metrics.min_fps,
            'max_fps': self._fps_metrics.max_fps,
            'custom': self._custom_metrics.copy(),
        }


# Global context
_stats_context = StatsContext()


def get_stats_context() -> StatsContext:
    """Get the global stats context."""
    return _stats_context


__all__ = ['FPSMetrics', 'StatsContext', 'get_stats_context']