"""
Transcript search utilities.

Search through conversation transcripts.
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def find_transcripts(directory: str) -> List[str]:
    """Find transcript files in directory.

    Args:
        directory: Directory to search

    Returns:
        List of transcript paths
    """
    transcripts = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".jsonl") or f.endswith(".transcript"):
                transcripts.append(os.path.join(root, f))
    return transcripts


def parse_transcript(path: str) -> List[Dict[str, Any]]:
    """Parse transcript file.

    Args:
        path: Transcript path

    Returns:
        List of messages
    """
    messages = []
    try:
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
    except Exception:
        pass
    return messages


def search_transcripts(
    transcripts: List[str],
    query: str,
) -> List[Dict[str, Any]]:
    """Search through transcripts.

    Args:
        transcripts: List of transcript paths
        query: Search query

    Returns:
        Matching messages
    """
    results = []
    query_lower = query.lower()

    for path in transcripts:
        messages = parse_transcript(path)
        for msg in messages:
            content = str(msg.get("content", ""))
            if query_lower in content.lower():
                results.append({
                    "transcript": path,
                    "message": msg,
                })

    return results


__all__ = [
    "find_transcripts",
    "parse_transcript",
    "search_transcripts",
]