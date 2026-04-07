# Web Fetch Tool Utils
# Reference: src/tools/WebFetchTool/utils.ts

from typing import Any, Dict, Optional
import re


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    match = re.search(r'https?://([^/]+)', url)
    return match.group(1) if match else None


def sanitize_html(html: str) -> str:
    """Remove potentially harmful HTML tags"""
    # Simple sanitization - remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    return html


def extract_text_from_html(html: str) -> str:
    """Extract text content from HTML"""
    # Remove script and style
    html = sanitize_html(html)
    # Replace tags with newlines
    html = re.sub(r'<[^>]+>', '\n', html)
    # Remove extra whitespace
    html = re.sub(r'\n+', '\n', html)
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    return html.strip()