"""
Escape XML/HTML special characters for safe interpolation.
"""

import html


def escape_xml(s: str) -> str:
    """Escape XML/HTML special characters for safe interpolation into element
    text content (between tags).
    """
    return html.escape(s, quote=False)


def escape_xml_attr(s: str) -> str:
    """Escape for interpolation into a double- or single-quoted attribute value."""
    return html.escape(s, quote=True)