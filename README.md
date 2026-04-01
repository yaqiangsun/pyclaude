# PyClaude

Python implementation of Claude Code - an AI programming assistant.

## Overview

PyClaude is a Python port of Claude Code, aiming to replicate the architecture and functionality of the original TypeScript project.

## Features

- **Core Query Engine** - Multi-turn conversation and tool calling support
- **Command System** - Complete command registration and execution framework
- **Bridge Remote Control** - Remote session control support
- **Multiple Transport Protocols** - WebSocket, SSE, Hybrid transport support
- **REPL Interactive Mode** - Interactive command-line interface

## Architecture

```
pyclaude/
├── __init__.py              # Package entry
├── __main__.py              # CLI entry
├── cli_main.py              # CLI main program
├── bootstrap/               # Initialization module
│   └── __init__.py
├── bridge/                  # Remote control module
│   ├── __init__.py
│   ├── bridge_main.py       # Bridge main controller
│   ├── repl_bridge.py       # REPL Bridge implementation
│   ├── session.py           # Session management
│   └── types.py             # Type definitions
├── cli/                     # CLI module
│   ├── __init__.py
│   ├── print.py             # Terminal output
│   ├── structured_io.py     # Structured I/O
│   └── transports/          # Transport layer
│       ├── __init__.py
│       ├── transport.py     # Base transport
│       ├── websocket.py     # WebSocket
│       ├── sse.py           # SSE
│       └── hybrid.py        # Hybrid
├── commands.py              # Command system
├── py_types/                # Type definitions
│   ├── __init__.py
│   └── ids.py               # ID types
├── query_engine.py          # Query engine
├── query.py                 # Query implementation
├── state/                   # State management
│   └── __init__.py
├── task.py                  # Task definition
├── tool.py                  # Tool definition
└── utils/                   # Utility functions
    ├── __init__.py
    ├── model/               # Model configuration
    │   └── model.py
    └── thinking.py          # Thinking configuration
```

## Installation

```bash
# Clone the project
git clone https://github.com/anthropics/claude-code.git
cd claude-code/pyclaude

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .
```

## Usage

### CLI Mode

```bash
# View help
python -m pyclaude --help

# Execute single query
python -m pyclaude "Write a hello world program"

# Specify model
python -m pyclaude -m claude-opus-4-20250501 "Your question"

# Verbose output
python -m pyclaude -v "Your question"

# Max turns limit
python -m pyclaude -n 5 "Your question"
```

### REPL Interactive Mode

```bash
python -m pyclaude --repl
```

### Programmatic Usage

```python
import asyncio
from pyclaude import QueryEngine, QueryEngineConfig
from pyclaude.tool import Tool

# Create a tool
class HelloTool(Tool):
    def __init__(self):
        super().__init__(
            name="hello",
            description="Say hello",
            input_schema={"type": "object", "properties": {"name": {"type": "string"}}}
        )

    async def execute(self, input_dict, get_app_state, set_app_state, abort_controller=None):
        name = input_dict.get("name", "World")
        return {"content": f"Hello, {name}!"}

# Run query
async def main():
    config = QueryEngineConfig(
        cwd="/path/to/project",
        tools=[HelloTool()],
        commands=[],
        mcp_clients=[],
        agents=[],
        can_use_tool=lambda *args: {"behavior": "allow"},
        get_app_state=lambda: {},
        set_app_state=lambda f: None,
    )

    engine = QueryEngine(config)

    async for message in engine.submit_message("Say hello to Alice"):
        print(message)

asyncio.run(main())
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `CLAUDE_MODEL` | Default model | claude-sonnet-4-20250514 |
| `CLAUDE_THINKING` | Thinking mode (true/false/disabled) | adaptive |
| `CLAUDE_DISABLE_PERSISTENCE` | Disable session persistence | false |

## Supported Models

- claude-opus-4-20250501
- claude-sonnet-4-20250514
- claude-haiku-4-20250307
- claude-3-5-sonnet-20240620

## Development

### Run Tests

```bash
pytest
```

### Code Style

```bash
# Lint
ruff check .

# Auto-fix
ruff check --fix .
```

## Comparison with Original

| Feature | TypeScript Original | Python Version |
|---------|---------------------|----------------|
| Core Engine | ✅ | ✅ |
| Command System | ✅ | ✅ |
| Bridge | ✅ | ✅ |
| Transport Layer | ✅ | ✅ |
| REPL | ✅ | ✅ |
| MCP Integration | ✅ | Planned |
| Complete Tool Set | ✅ | Planned |
| UI Components | React/Ink | textual (planned) |

## License

MIT License - Same as original Claude Code

## References

- [Claude Code Official Repository](https://github.com/anthropics/claude-code)
- [Anthropic API Documentation](https://docs.anthropic.com)