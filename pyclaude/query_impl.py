"""
Query implementation - handles the actual message loop and tool execution.
"""

import asyncio
from typing import Any, AsyncGenerator, Optional, Union


async def query(
    prompt: Union[str, list[dict]],
    messages: list[dict],
    tools: list[Any],
    commands: list[Any],
    mcp_clients: list[Any],
    agents: list[Any],
    can_use_tool: callable,
    get_app_state: callable,
    set_app_state: callable,
    system_prompt: str,
    user_context: str,
    system_context: dict,
    thinking_config: dict,
    max_turns: Optional[int] = None,
    max_budget_usd: Optional[float] = None,
    task_budget: Optional[dict] = None,
    json_schema: Optional[dict] = None,
    verbose: bool = False,
    replay_user_messages: bool = False,
    include_partial_messages: bool = False,
    set_sdk_status: Optional[callable] = None,
    abort_controller: Any = None,
    orphaned_permission: Optional[dict] = None,
    read_file_state: Optional[dict] = None,
) -> AsyncGenerator[dict, None]:
    """
    Main query loop - handles message building, tool execution, and API calls.

    Args:
        prompt: User prompt (string or content blocks)
        messages: Existing conversation messages
        tools: Available tools
        commands: Available commands
        mcp_clients: MCP server connections
        agents: Available agents
        can_use_tool: Function to check tool permissions
        get_app_state: Function to get app state
        set_app_state: Function to set app state
        system_prompt: System prompt
        user_context: User context
        system_context: System context
        thinking_config: Thinking configuration
        max_turns: Maximum turns in conversation
        max_budget_usd: Maximum budget in USD
        task_budget: Task budget configuration
        json_schema: JSON schema for output
        verbose: Verbose logging
        replay_user_messages: Replay user messages
        include_partial_messages: Include partial messages
        set_sdk_status: SDK status callback
        abort_controller: Abort controller
        orphaned_permission: Orphaned permission
        read_file_state: File state cache

    Yields:
        SDK messages as the query progresses
    """
    read_file_state = read_file_state or {}
    abort_controller = abort_controller or AbortController()
    turn_count = 0

    # Build user message
    user_message = _build_user_message(prompt)

    # Add to messages
    messages = list(messages)
    messages.append(user_message)

    # Main loop
    while True:
        # Check abort
        if abort_controller.is_aborted:
            yield {'type': 'error', 'error': 'aborted'}
            break

        # Check max turns
        if max_turns and turn_count >= max_turns:
            yield {'type': 'error', 'error': 'max_turns_reached'}
            break

        turn_count += 1

        # Call API
        response = await _call_api(
            messages=messages,
            tools=tools,
            system_prompt=system_prompt,
            user_context=user_context,
            thinking_config=thinking_config,
            json_schema=json_schema,
            verbose=verbose,
        )

        # Yield response message
        yield {'type': 'message', 'message': response}

        # Add assistant message to history
        messages.append(response)

        # Process tool uses
        tool_uses = _extract_tool_uses(response)

        if not tool_uses:
            # No more tool uses, we're done
            break

        # Execute tools
        for tool_use in tool_uses:
            # Check permission
            permission_result = await can_use_tool(
                tool=tool_use['name'],
                input_dict=tool_use['input'],
                tool_use_context={},
                assistant_message=response,
                tool_use_id=tool_use['id'],
            )

            if permission_result.get('behavior') == 'deny':
                # Tool was denied
                tool_result = {
                    'type': 'tool_result',
                    'tool_use_id': tool_use['id'],
                    'content': f"Tool '{tool_use['name']}' was denied",
                    'is_error': True,
                }
                yield {'type': 'tool_result', 'result': tool_result}
                messages.append(tool_result)
                continue

            # Execute tool
            result = await _execute_tool(
                tool_name=tool_use['name'],
                tool_input=tool_use['input'],
                tools=tools,
                commands=commands,
                mcp_clients=mcp_clients,
                get_app_state=get_app_state,
                set_app_state=set_app_state,
                abort_controller=abort_controller,
            )

            # Yield tool result
            tool_result = {
                'type': 'tool_result',
                'tool_use_id': tool_use['id'],
                'content': result.get('content', ''),
                'is_error': result.get('is_error', False),
            }
            yield {'type': 'tool_result', 'result': tool_result}

            # Add to messages
            messages.append(tool_result)


def _build_user_message(prompt: Union[str, list[dict]]) -> dict:
    """Build a user message from prompt."""
    if isinstance(prompt, str):
        return {'type': 'message', 'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}
    return {'type': 'message', 'role': 'user', 'content': prompt}


async def _call_api(
    messages: list[dict],
    tools: list[Any],
    system_prompt: str,
    user_context: str,
    thinking_config: dict,
    json_schema: Optional[dict],
    verbose: bool,
) -> dict:
    """Call the Anthropic API."""
    # This is a placeholder - the actual implementation would use httpx
    # to call the Anthropic API
    from .services.api import call_anthropic_api

    api_messages = [
        {'role': 'system', 'content': system_prompt + '\n\n' + user_context}
    ]
    api_messages.extend(messages)

    response = await call_anthropic_api(
        messages=api_messages,
        tools=tools,
        thinking_config=thinking_config,
        json_schema=json_schema,
    )

    return response


def _extract_tool_uses(response: dict) -> list[dict]:
    """Extract tool uses from response."""
    tool_uses = []
    content = response.get('content', [])

    for block in content:
        if block.get('type') == 'tool_use':
            tool_uses.append({
                'id': block.get('id'),
                'name': block.get('name'),
                'input': block.get('input', {}),
            })

    return tool_uses


async def _execute_tool(
    tool_name: str,
    tool_input: dict,
    tools: list[Any],
    commands: list[Any],
    mcp_clients: list[Any],
    get_app_state: callable,
    set_app_state: callable,
    abort_controller: Any,
) -> dict:
    """Execute a tool."""
    # Find the tool
    tool = None
    for t in tools:
        if t.name == tool_name:
            tool = t
            break

    if not tool:
        return {'content': f"Tool '{tool_name}' not found", 'is_error': True}

    # Execute the tool
    try:
        result = await tool.execute(tool_input, get_app_state, set_app_state, abort_controller)
        return result
    except Exception as e:
        return {'content': str(e), 'is_error': True}


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
__all__ = ['query', 'AbortController']