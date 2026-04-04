"""Tests for task module."""
import pytest
from pyclaude.task import (
    TaskType,
    TaskStatus,
    generate_task_id,
    is_terminal_task_status,
    AbortController,
)


class TestTaskType:
    """Test TaskType enum."""

    def test_task_types_exist(self):
        """All expected task types exist."""
        assert TaskType.LOCAL_BASH == 'local_bash'
        assert TaskType.LOCAL_AGENT == 'local_agent'
        assert TaskType.REMOTE_AGENT == 'remote_agent'
        assert TaskType.IN_PROCESS_TEAMMATE == 'in_process_teammate'
        assert TaskType.LOCAL_WORKFLOW == 'local_workflow'
        assert TaskType.MONITOR_MCP == 'monitor_mcp'
        assert TaskType.DREAM == 'dream'


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_task_statuses_exist(self):
        """All expected task statuses exist."""
        assert TaskStatus.PENDING == 'pending'
        assert TaskStatus.RUNNING == 'running'
        assert TaskStatus.COMPLETED == 'completed'
        assert TaskStatus.FAILED == 'failed'
        assert TaskStatus.KILLED == 'killed'


class TestGenerateTaskId:
    """Test task ID generation."""

    def test_generate_task_id_format(self):
        """Task ID has correct prefix and length."""
        task_id = generate_task_id(TaskType.LOCAL_BASH)
        assert task_id.startswith('b')
        assert len(task_id) == 9  # prefix + 8 chars

    def test_generate_task_id_unique(self):
        """Generated IDs are unique."""
        ids = [generate_task_id(TaskType.LOCAL_AGENT) for _ in range(100)]
        assert len(set(ids)) == 100


class TestIsTerminalTaskStatus:
    """Test terminal status detection."""

    def test_completed_is_terminal(self):
        """COMPLETED is terminal."""
        assert is_terminal_task_status(TaskStatus.COMPLETED) is True

    def test_failed_is_terminal(self):
        """FAILED is terminal."""
        assert is_terminal_task_status(TaskStatus.FAILED) is True

    def test_killed_is_terminal(self):
        """KILLED is terminal."""
        assert is_terminal_task_status(TaskStatus.KILLED) is True

    def test_pending_is_not_terminal(self):
        """PENDING is not terminal."""
        assert is_terminal_task_status(TaskStatus.PENDING) is False

    def test_running_is_not_terminal(self):
        """RUNNING is not terminal."""
        assert is_terminal_task_status(TaskStatus.RUNNING) is False


class TestAbortController:
    """Test AbortController."""

    def test_initially_not_aborted(self):
        """Controller starts not aborted."""
        controller = AbortController()
        assert controller.is_aborted is False

    def test_abort_sets_flag(self):
        """abort() sets the aborted flag."""
        controller = AbortController()
        controller.abort()
        assert controller.is_aborted is True