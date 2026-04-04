"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add pyclaude to path
pyclaude_path = Path(__file__).parent.parent / "pyclaude"
sys.path.insert(0, str(pyclaude_path))


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Test response"}],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
    }