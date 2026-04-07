# Web Fetch Tool - Fetch content from URLs
# Reference: src/tools/WebFetchTool/WebFetchTool.ts

from typing import Any, Dict, Optional
from dataclasses import dataclass


WEB_FETCH_TOOL_NAME = "WebFetch"

DESCRIPTION = """- Use this tool to fetch content from URLs
- Fetches web page content and processes it using AI
- Supports URL validation and content extraction"""


@dataclass
class WebFetchInput:
    """Input schema for WebFetchTool"""
    url: str
    prompt: Optional[str] = None


@dataclass
class WebFetchOutput:
    """Output schema for WebFetchTool"""
    content: str
    url: str
    title: Optional[str] = None


class WebFetchTool:
    """Tool for fetching web content"""

    name: str = WEB_FETCH_TOOL_NAME
    description: str = DESCRIPTION
    should_defer: bool = True

    def __init__(self):
        pass

    async def validate_input(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate input parameters"""
        url = input_data.get("url")
        if not url:
            return {
                "result": False,
                "message": "Missing required parameter: url",
                "error_code": 1
            }

        # Check URL format
        if not url.startswith(("http://", "https://")):
            return {
                "result": False,
                "message": "Invalid URL format",
                "error_code": 2
            }

        return {"result": True}

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute web fetch"""
        url = input_data.get("url")
        prompt = input_data.get("prompt")

        if not url:
            return {"success": False, "error": "Missing url parameter"}

        # Placeholder - actual implementation would use requests/httpx
        return {
            "success": True,
            "content": f"Content from {url}",
            "url": url
        }


web_fetch_tool = WebFetchTool()