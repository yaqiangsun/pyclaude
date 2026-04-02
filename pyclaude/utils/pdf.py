"""
PDF utilities.

PDF processing helpers.
"""

import os
from typing import Optional, List, Dict, Any


def is_pdf(path: str) -> bool:
    """Check if file is PDF.

    Args:
        path: File path

    Returns:
        True if PDF
    """
    return path.lower().endswith(".pdf")


def extract_pdf_text(path: str) -> Optional[str]:
    """Extract text from PDF.

    Args:
        path: PDF file path

    Returns:
        Extracted text or None
    """
    # Placeholder - would use PyPDF2 or similar
    return None


def get_pdf_info(path: str) -> Optional[Dict[str, Any]]:
    """Get PDF metadata.

    Args:
        path: PDF file path

    Returns:
        PDF info dict
    """
    # Placeholder
    return None


__all__ = [
    "is_pdf",
    "extract_pdf_text",
    "get_pdf_info",
]