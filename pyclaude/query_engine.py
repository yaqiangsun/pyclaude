"""
QueryEngine - Core orchestrator for AI interactions.

Manages the query lifecycle and session state for a conversation.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Optional, Union

from .state import AppState
from .tool import Tool, ToolPermissionContext


@dataclass
class QueryEngineConfig:
    """Configuration for QueryEngine."""
    cwd: str
    tools: list[Tool]
    commands: list[Any]
    mcp_clients: list[Any]
    agents: list[Any]
    can_use_tool: Callable
    get_app_state: Callable[[], AppState]
    set_app_state: Callable[[Callable[[AppState], AppState]], None]
    initial_messages: list[dict] = field(default_factory=list)
    read_file_cache: dict = field(default_factory=dict)
    custom_system_prompt: Optional[str] = None
    append_system_prompt: Optional[str] = None
    user_specified_model: Optional[str] = None
    fallback_model: Optional[str] = None
    thinking_config: Optional[dict] = None
    max_turns: Optional[int] = None
    max_budget_usd: Optional[float] = None
    task_budget: Optional[dict] = None
    json_schema: Optional[dict] = None
    verbose: bool = False
    replay_user_messages: bool = False
    handle_elicitation: Optional[Callable] = None
    include_partial_messages: bool = False
    set_sdk_status: Optional[Callable[[dict], None]] = None
    abort_controller: Any = None
    orphaned_permission: Optional[dict] = None
    snip_replay: Optional[Callable] = None


class QueryEngine:
    """
    QueryEngine owns the query lifecycle and session state for a conversation.

    It extracts the core logic from ask() into a standalone class that can be
    used by both the headless/SDK path and the REPL.

    One QueryEngine per conversation. Each submitMessage() call starts a new
    turn within the same conversation. State (messages, file cache, usage, etc.)
    persists across turns.
    """

    def __init__(self, config: QueryEngineConfig):
        self.config = config
        self.mutable_messages = list(config.initial_messages or [])
        self.abort_controller = config.abort_controller or AbortController()
        self.permission_denials: list[dict] = []
        self.read_file_state = config.read_file_cache or {}
        self.total_usage: dict = {}
        self.has_handled_orphaned_permission = False
        self.discovered_skill_names: set[str] = set()
        self.loaded_nested_memory_paths: set[str] = set()

    async def submit_message(
        self,
        prompt: Union[str, list[dict]],
        options: Optional[dict] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Submit a message and yield SDK messages as they arrive.

        Args:
            prompt: The user prompt (string or content blocks)
            options: Optional parameters (uuid, is_meta)

        Yields:
            SDK messages as the query progresses
        """
        options = options or {}
        uuid = options.get('uuid')
        is_meta = options.get('is_meta', False)

        # Get configuration
        cwd = self.config.cwd
        commands = self.config.commands
        tools = self.config.tools
        mcp_clients = self.config.mcp_clients
        verbose = self.config.verbose
        thinking_config = self.config.thinking_config
        max_turns = self.config.max_turns
        max_budget_usd = self.config.max_budget_usd
        task_budget = self.config.task_budget
        can_use_tool = self.config.can_use_tool
        custom_system_prompt = self.config.custom_system_prompt
        append_system_prompt = self.config.append_system_prompt
        user_specified_model = self.config.user_specified_model
        fallback_model = self.config.fallback_model
        json_schema = self.config.json_schema
        get_app_state = self.config.get_app_state
        set_app_state = self.config.set_app_state
        replay_user_messages = self.config.replay_user_messages
        include_partial_messages = self.config.include_partial_messages
        agents = self.config.agents
        set_sdk_status = self.config.set_sdk_status
        orphaned_permission = self.config.orphaned_permission

        # Clear discovered skills at start of each submitMessage
        self.discovered_skill_names.clear()

        # Get initial app state
        initial_app_state = get_app_state()
        initial_main_loop_model = user_specified_model or self._get_main_loop_model()

        # Determine thinking config
        if thinking_config:
            initial_thinking_config = thinking_config
        else:
            from .utils.thinking import should_enable_thinking_by_default
            enabled = should_enable_thinking_by_default()
            if enabled is not False:
                initial_thinking_config = {'type': 'adaptive'}
            else:
                initial_thinking_config = {'type': 'disabled'}

        # Wrap canUseTool to track permission denials
        async def wrapped_can_use_tool(
            tool: Tool,
            input_dict: dict,
            tool_use_context: dict,
            assistant_message: dict,
            tool_use_id: str,
            force_decision: bool = False,
        ) -> dict:
            result = await can_use_tool(
                tool,
                input_dict,
                tool_use_context,
                assistant_message,
                tool_use_id,
                force_decision,
            )

            # Track denials for SDK reporting
            if result.get('behavior') != 'allow':
                self.permission_denials.append({
                    'tool_name': tool.name,
                    'tool_use_id': tool_use_id,
                    'tool_input': input_dict,
                })

            return result

        # Build system prompt and context
        from .utils.query_context import fetch_system_prompt_parts

        custom_prompt = custom_system_prompt if isinstance(custom_system_prompt, str) else None
        prompt_parts = await fetch_system_prompt_parts(
            tools=tools,
            main_loop_model=initial_main_loop_model,
            additional_working_directories=list(
                initial_app_state.tool_permission_context.additional_working_directories.keys()
            ) if hasattr(initial_app_state, 'tool_permission_context') else [],
            mcp_clients=mcp_clients,
            custom_system_prompt=custom_prompt,
            append_system_prompt=append_system_prompt,
        )

        default_system_prompt = prompt_parts.get('default_system_prompt', '')
        base_user_context = prompt_parts.get('user_context', '')
        system_context = prompt_parts.get('system_context', {})

        # Build the query and execute
        # Import query function from query_impl module
        from pyclaude.query_impl import query

        async for message in query(
            prompt=prompt,
            messages=self.mutable_messages,
            tools=tools,
            commands=commands,
            mcp_clients=mcp_clients,
            agents=agents,
            can_use_tool=wrapped_can_use_tool,
            get_app_state=get_app_state,
            set_app_state=set_app_state,
            system_prompt=default_system_prompt,
            user_context=base_user_context,
            system_context=system_context,
            thinking_config=initial_thinking_config,
            max_turns=max_turns,
            max_budget_usd=max_budget_usd,
            task_budget=task_budget,
            json_schema=json_schema,
            verbose=verbose,
            replay_user_messages=replay_user_messages,
            include_partial_messages=include_partial_messages,
            set_sdk_status=set_sdk_status,
            abort_controller=self.abort_controller,
            orphaned_permission=orphaned_permission,
            read_file_state=self.read_file_state,
        ):
            yield message

    def _get_main_loop_model(self) -> str:
        """Get the main loop model setting."""
        from .utils.model import get_main_loop_model
        return get_main_loop_model()

    def get_messages(self) -> list[dict]:
        """Get the current messages."""
        return list(self.mutable_messages)

    def get_usage(self) -> dict:
        """Get the total usage."""
        return self.total_usage

    def get_permission_denials(self) -> list[dict]:
        """Get the tracked permission denials."""
        return list(self.permission_denials)


class AbortController:
    """Simple abort controller."""

    def __init__(self):
        self._aborted = False

    def abort(self):
        self._aborted = True

    @property
    def is_aborted(self) -> bool:
        return self._aborted


# Export
__all__ = ['QueryEngine', 'QueryEngineConfig', 'AbortController']