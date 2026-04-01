"""
Leaf stripBOM — extracted from json.ts to break settings → json → log →
types/logs → … → settings.

UTF-8 BOM (U+FEFF): PowerShell 5.x writes UTF-8 with BOM by default
(Out-File, Set-Content). We can't control user environments, so strip on
read. Without this, JSON.parse fails with "Unexpected token".
"""

from typing import Any, Optional
import json


UTF8_BOM = '\uFEFF'


def strip_bom(content: str) -> str:
    """Strip UTF-8 BOM from content if present."""
    return content[1:] if content.startswith(UTF8_BOM) else content


def json_read(content: str) -> Any:
    """Parse JSON string, stripping BOM if present."""
    return json.loads(strip_bom(content))


def safe_json_read(content: str) -> Optional[Any]:
    """Safely parse JSON string, returning None on error."""
    try:
        return json_read(content)
    except (json.JSONDecodeError, ValueError):
        return None