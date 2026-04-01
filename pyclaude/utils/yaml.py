"""
YAML parsing wrapper.

Uses PyYAML for Python. The package is lazy-imported to avoid loading
if not needed.
"""

from typing import Any, Optional


def parse_yaml(input: str) -> Any:
    """Parse YAML input string."""
    try:
        import yaml
        return yaml.safe_load(input)
    except ImportError:
        raise ImportError("PyYAML is required. Install with: pip install pyyaml")


def dump_yaml(data: Any) -> str:
    """Dump data to YAML string."""
    try:
        import yaml
        return yaml.dump(data, default_flow_style=False)
    except ImportError:
        raise ImportError("PyYAML is required. Install with: pip install pyyaml")