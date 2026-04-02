"""
Heatmap utilities.

Generate heatmap visualizations.
"""

from typing import List, Tuple, Optional


def generate_heatmap(
    data: List[List[float]],
    width: int = 40,
    height: int = 10,
) -> str:
    """Generate ASCII heatmap.

    Args:
        data: 2D array of values (0-1)
        width: Output width
        height: Output height

    Returns:
        ASCII heatmap string
    """
    if not data:
        return ""

    # Simple heatmap using block characters
    blocks = " ░▒▓█"

    result = []
    for row in data[:height]:
        line = ""
        for val in row[:width]:
            idx = int(val * (len(blocks) - 1))
            line += blocks[idx]
        result.append(line)

    return "\n".join(result)


def color_to_value(r: int, g: int, b: int) -> float:
    """Convert RGB to normalized value.

    Args:
        r, g, b: Color components (0-255)

    Returns:
        Normalized value (0-1)
    """
    return (r + g + b) / (255 * 3)


__all__ = [
    "generate_heatmap",
    "color_to_value",
]