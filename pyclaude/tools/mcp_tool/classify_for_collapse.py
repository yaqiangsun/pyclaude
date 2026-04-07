# MCP Tool Classify For Collapse
# Reference: src/tools/MCPTool/classifyForCollapse.ts

from typing import Any, Dict, List, Optional


def classify_for_collapse(results: List[Any]) -> Dict[str, Any]:
    """Classify MCP results for collapsible display"""
    if not results:
        return {"type": "empty"}

    # Check if results are collapsible
    if len(results) > 3:
        return {
            "type": "collapsible",
            "summary": f"{len(results)} items",
            "expanded": False
        }

    return {
        "type": "expanded",
        "expanded": True
    }


def should_collapse_mcp_result(result: Any) -> bool:
    """Determine if MCP result should be collapsed"""
    if isinstance(result, dict):
        # Collapse if has many keys
        return len(result.keys()) > 5
    if isinstance(result, list):
        return len(result) > 3
    return False