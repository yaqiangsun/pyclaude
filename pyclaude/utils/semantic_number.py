"""
Semantic number utilities.

Number parsing with semantic meaning.
"""

from typing import Optional, Union


def parse_number(value: Union[str, int, float]) -> Optional[float]:
    """Parse value to number.

    Args:
        value: Value to parse

    Returns:
        Number or None if cannot parse
    """
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        # Handle suffixes like K, M, G, T
        suffixes = {
            "k": 1e3,
            "m": 1e6,
            "g": 1e9,
            "t": 1e12,
        }
        lower = value.lower().strip()
        for suffix, multiplier in suffixes.items():
            if lower.endswith(suffix):
                try:
                    return float(lower[:-1]) * multiplier
                except ValueError:
                    pass

        try:
            return float(value)
        except ValueError:
            pass

    return None


def parse_bytes(value: str) -> Optional[int]:
    """Parse byte string to integer.

    Args:
        value: Byte string (e.g., "1KB", "2MB")

    Returns:
        Byte count or None
    """
    suffixes = {
        "b": 1,
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
        "tb": 1024**4,
    }

    lower = value.lower().strip()
    for suffix, multiplier in suffixes.items():
        if lower.endswith(suffix):
            try:
                num = float(lower[:-len(suffix)].strip())
                return int(num * multiplier)
            except ValueError:
                pass

    return None


__all__ = [
    "parse_number",
    "parse_bytes",
]