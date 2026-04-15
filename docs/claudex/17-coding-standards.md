# 17 - 代码规范

本文档定义 Python 版本项目的代码规范，包括代码风格、测试规范、示例代码规范等。

---

## 17.1 项目结构规范

### 17.1.1 目录结构

```
pyclaude/
├── pyclaude/                      # 主包
│   ├── __init__.py                # 包初始化，导出主要 API
│   ├── __main__.py                # 入口点：python -m pyclaude
│   ├── main.py                    # 主程序
│   ├── config.py                  # 配置管理
│   ├── engine.py                  # QueryEngine
│   ├── core/                      # 核心模块
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── query.py
│   │   ├── history.py
│   │   └── context.py
│   ├── tools/                     # 工具系统
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── bash.py
│   │   ├── file.py
│   │   ├── glob.py
│   │   ├── grep.py
│   │   ├── agent.py
│   │   └── permissions.py
│   ├── commands/                  # 命令系统
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── base.py
│   │   ├── loader.py
│   │   ├── commit.py
│   │   ├── config.py
│   │   └── branch.py
│   ├── skills/                    # 技能系统
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── loader.py
│   │   └── builtin/
│   │       ├── __init__.py
│   │       ├── simplify.py
│   │       ├── debug.py
│   │       └── verify.py
│   ├── bridge/                    # Bridge 模块
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── session.py
│   │   └── transport/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── websocket.py
│   │       ├── sse.py
│   │       └── hybrid.py
│   ├── cli/                       # CLI 应用
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── completion.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── message.py
│   │   │   ├── tool_result.py
│   │   │   └── progress.py
│   │   └── input/
│   │       ├── __init__.py
│   │       ├── keybindings.py
│   │       ├── vim.py
│   │       └── server.py
│   ├── services/                  # 服务层
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── mcp.py
│   │   ├── analytics.py
│   │   ├── model.py
│   │   └── compact.py
│   ├── state/                     # 状态管理
│   │   ├── __init__.py
│   │   ├── store.py
│   │   ├── app_state.py
│   │   └── selectors.py
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── bash.py
│   │   ├── git.py
│   │   ├── permissions.py
│   │   ├── messages.py
│   │   ├── model.py
│   │   └── files.py
│   ├── constants/                 # 常量
│   │   ├── __init__.py
│   │   ├── api_limits.py
│   │   ├── tool_limits.py
│   │   ├── prompts.py
│   │   └── keybindings.py
│   ├── buddy/                     # Buddy 模块
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── sprite.py
│   ├── coordinator/               # Coordinator 模块
│   │   ├── __init__.py
│   │   └── task_coordinator.py
│   ├── memdir/                    # Memdir 模块
│   │   ├── __init__.py
│   │   ├── memory.py
│   │   └── entries.py
│   └── remote/                    # Remote 模块
│       ├── __init__.py
│       ├── session.py
│       └── manager.py
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── conftest.py                # pytest 配置
│   ├── unit/                      # 单元测试
│   │   ├── __init__.py
│   │   ├── test_core/
│   │   ├── test_tools/
│   │   ├── test_commands/
│   │   └── test_services/
│   ├── integration/               # 集成测试
│   │   ├── __init__.py
│   │   └── test_engine.py
│   └── fixtures/                  # 测试 fixtures
│       ├── __init__.py
│       └── mock_*.py
├── examples/                      # 示例代码
│   ├── __init__.py
│   ├── basic/
│   │   ├── __init__.py
│   │   ├── simple_query.py
│   │   └── tool_usage.py
│   ├── advanced/
│   │   ├── __init__.py
│   │   ├── custom_tool.py
│   │   └── custom_command.py
│   └── scripts/
│       ├── __init__.py
│       └── batch_query.py
├── docs/                          # 文档
├── pyproject.toml                 # 项目配置
├── setup.py                       # 安装脚本
├── requirements.txt               # 依赖
├── requirements-dev.txt           # 开发依赖
├── requirements-test.txt          # 测试依赖
├── .pre-commit-config.yaml        # pre-commit 配置
├── Makefile                       # 构建脚本
└── README.md                      # 项目说明
```

### 17.1.2 模块命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 包 | 全部小写，下划线分隔 | `pyclaude.tools` |
| 模块 | 全部小写，下划线分隔 | `bash.py`, `file_edit.py` |
| 类 | PascalCase | `QueryEngine`, `BaseTool` |
| 函数 | snake_case | `get_tool()`, `run_bash()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_TOKENS`, `DEFAULT_MODEL` |
| 私有成员 | 前缀单下划线 | `_private_method()` |
| 内部模块 | 前缀下划线 | `_internal/` |

---

## 17.2 代码风格规范

### 17.2.1 格式化工具

| 工具 | 配置 | 用途 |
|------|------|------|
| `ruff` | `pyproject.toml` | 格式化 + Lint |
| `black` | `pyproject.toml` | 代码格式化 |
| `isort` | `pyproject.toml` | import 排序 |
| `mypy` | `mypy.ini` | 类型检查 |
| `pyright` | `pyrightconfig.json` | 类型检查 |

### 17.2.2 格式化配置 (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]  # 行长度由 black 处理

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.isort]
profile = "black"
line-length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 17.2.3 代码风格要点

#### Import 排序
```python
# 标准库
import os
import sys
from pathlib import Path
from typing import Optional, Any

# 第三方库
import httpx
from pydantic import BaseModel
from prompt_toolkit import PromptSession

# 本地包
from pyclaude.core.task import Task, TaskType
from pyclaude.tools.base import BaseTool
from pyclaude.tools.registry import ToolRegistry
```

#### 类型注解
```python
# 推荐：使用类型注解
def get_tool(self, name: str) -> Optional[BaseTool]:
    """获取工具"""
    return self.tools.get(name)

# 复杂类型使用 TypeAlias
MessageList: TypeAlias = list[dict[str, Any]]

# 泛型
class Store(Generic[T]):
    def __init__(self, initial_state: Optional[T] = None) -> None:
        ...
```

#### 文档字符串
```python
def execute(self, tool_input: dict[str, Any]) -> dict[str, Any]:
    """执行工具.

    Args:
        tool_input: 工具输入参数

    Returns:
        包含执行结果的字典

    Raises:
        ValueError: 工具输入无效
        ToolExecutionError: 工具执行失败
    """
    ...
```

---

## 17.3 测试规范

### 17.3.1 测试框架

| 框架 | 用途 |
|------|------|
| `pytest` | 主测试框架 |
| `pytest-asyncio` | 异步测试 |
| `pytest-mock` | Mock 工具 |
| `pytest-cov` | 覆盖率 |

### 17.3.2 测试文件结构

```
tests/
├── unit/                      # 单元测试
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_task.py
│   │   ├── test_history.py
│   │   └── test_context.py
│   ├── test_tools/
│   │   ├── __init__.py
│   │   ├── test_bash.py
│   │   ├── test_file.py
│   │   ├── test_glob.py
│   │   ├── test_grep.py
│   │   └── test_registry.py
│   ├── test_commands/
│   │   ├── __init__.py
│   │   ├── test_registry.py
│   │   └── test_commit.py
│   └── test_services/
│       ├── __init__.py
│       ├── test_api.py
│       └── test_mcp.py
├── integration/               # 集成测试
│   ├── __init__.py
│   ├── test_engine.py
│   ├── test_query_loop.py
│   └── test_bridge.py
└── fixtures/                  # 测试 fixtures
    ├── __init__.py
    ├── mock_api.py
    ├── mock_tools.py
    └── sample_files/
```

### 17.3.3 单元测试规范

```python
# tests/unit/test_tools/test_bash.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from pyclaude.tools.bash import BashTool


class TestBashTool:
    """BashTool 单元测试"""

    @pytest.fixture
    def tool(self) -> BashTool:
        """创建工具实例"""
        return BashTool()

    def test_get_definition(self, tool: BashTool) -> None:
        """测试获取工具定义"""
        definition = tool.get_definition()

        assert definition.name == "bash"
        assert definition.capability == ToolCapability.DESTRUCTIVE

    @pytest.mark.asyncio
    async def test_execute_success(self, tool: BashTool) -> None:
        """测试成功执行命令"""
        tool_input = {"command": "echo hello", "description": "Test command"}

        result = await tool.execute(tool_input)

        assert result["success"] is True
        assert "hello" in result["stdout"]

    @pytest.mark.asyncio
    async def test_execute_failure(self, tool: BashTool) -> None:
        """测试命令执行失败"""
        tool_input = {"command": "exit 1"}

        result = await tool.execute(tool_input)

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_permission_dangerous_command(self, tool: BashTool) -> None:
        """测试危险命令权限检查"""
        tool_input = {"command": "rm -rf /"}

        permission = await tool.check_permission(tool_input)

        assert permission.allowed is False
        assert "dangerous" in permission.reason.lower()
```

### 17.3.4 集成测试规范

```python
# tests/integration/test_engine.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from pyclaude.engine import QueryEngine, QueryEngineConfig
from pyclaude.tools.registry import ToolRegistry
from pyclaude.commands.registry import CommandRegistry
from pyclaude.state.store import Store
from pyclaude.state.app_state import AppState
from pyclaude.services.api import APIClient


class TestQueryEngine:
    """QueryEngine 集成测试"""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """创建模拟 API 客户端"""
        client = MagicMock(spec=APIClient)
        client.stream = AsyncMock(return_value=iter([
            {"type": "content_block", "text": "Hello!"},
            {"type": "content_block", "text": " How can I help?"},
        ]))
        return client

    @pytest.fixture
    def engine(
        self,
        mock_api_client: MagicMock,
    ) -> QueryEngine:
        """创建引擎实例"""
        return QueryEngine(
            api_client=mock_api_client,
            tool_registry=ToolRegistry(),
            command_registry=CommandRegistry(),
            store=Store(AppState()),
        )

    @pytest.mark.asyncio
    async def test_query_basic(self, engine: QueryEngine) -> None:
        """测试基本查询"""
        chunks = []
        async for chunk in engine.query("Hello"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert chunks[0].get("type") == "content_block"
```

### 17.3.5 测试覆盖率要求

| 指标 | 目标 |
|------|------|
| 总覆盖率 | ≥ 80% |
| 核心模块覆盖率 | ≥ 90% |
| 新功能覆盖率 | 100% |

---

## 17.4 示例代码规范

### 17.4.1 示例目录结构

```
examples/
├── basic/                      # 基础示例
│   ├── __init__.py
│   ├── simple_query.py         # 简单查询
│   ├── tool_usage.py           # 工具使用
│   ├── command_execution.py    # 命令执行
│   └── history_management.py   # 历史管理
├── advanced/                   # 高级示例
│   ├── __init__.py
│   ├── custom_tool.py          # 自定义工具
│   ├── custom_command.py       # 自定义命令
│   ├── custom_skill.py         # 自定义技能
│   └── bridge_connection.py    # Bridge 连接
└── scripts/                    # 实用脚本
    ├── __init__.py
    ├── batch_query.py          # 批量查询
    ├── session_resume.py       # 会话恢复
    └── context_export.py       # 上下文导出
```

### 17.4.2 基础示例规范

```python
# examples/basic/simple_query.py
"""
简单查询示例

本示例展示如何使用 Python SDK 进行简单的 AI 对话。
"""

import asyncio
from pyclaude import ClaudeClient


async def main() -> None:
    """主函数"""
    # 初始化客户端
    client = ClaudeClient(api_key="your-api-key")

    # 发送查询
    print("Sending query to Claude...")
    async for response in client.query("Hello, how are you?"):
        print(response.text, end="")

    print("\n\nQuery completed!")


if __name__ == "__main__":
    asyncio.run(main())
```

### 17.4.3 高级示例规范

```python
# examples/advanced/custom_tool.py
"""
自定义工具示例

本示例展示如何创建自定义工具并注册到工具注册表中。
"""

import asyncio
from pyclaude.tools.base import BaseTool, ToolDefinition, ToolCapability
from pyclaude.tools.registry import ToolRegistry


class CustomWeatherTool(BaseTool):
    """自定义天气查询工具"""

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="weather",
            description="查询指定城市的天气",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            },
            capability=ToolCapability.READ_ONLY,
        )

    async def execute(self, tool_input: dict) -> dict:
        city = tool_input.get("city", "")
        # 实现天气查询逻辑
        return {
            "city": city,
            "weather": "sunny",
            "temperature": 25,
        }


async def main() -> None:
    """演示自定义工具"""
    # 创建注册表
    registry = ToolRegistry()

    # 注册自定义工具
    custom_tool = CustomWeatherTool()
    registry.register(custom_tool)

    # 使用工具
    tool = registry.get("weather")
    result = await tool.execute({"city": "Beijing"})
    print(f"Weather in Beijing: {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 17.4.4 示例代码要求

| 要求 | 说明 |
|------|------|
| 完整可运行 | 所有示例必须可以直接运行 |
| 注释完整 | 包含模块级和函数级文档字符串 |
| 错误处理 | 包含适当的异常处理 |
| 类型注解 | 所有函数必须包含类型注解 |
| 路径规范 | 使用相对导入，从 pyclaude 包导入 |

---

## 17.5 提交规范

### 17.5.1 Git 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型 (type):
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例:
```
feat(tools): add WebFetchTool for fetching web content

- Implement HTTP GET/POST support
- Add response parsing
- Support JSON and HTML formats

Closes #123
```

### 17.5.2 Commit 钩子配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
```

---

## 17.6 发布规范

### 17.6.1 版本号管理

采用语义化版本 (Semantic Versioning):

```
MAJOR.MINOR.PATCH
```

- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的新功能
- PATCH: 向后兼容的 Bug 修复

### 17.6.2 发布检查清单

- [ ] 所有测试通过 (`pytest`)
- [ ] 覆盖率达标 (≥ 80%)
- [ ] 类型检查通过 (`mypy`)
- [ ] 代码格式检查通过 (`ruff`)
- [ ] 文档更新
- [ ] CHANGELOG 更新
- [ ] 版本号更新
- [ ] 构建发布包 (`build`)

---

## 17.7 模块接口清单

| 规范项 | 文件 |
|--------|------|
| 项目结构 | `pyproject.toml` |
| 格式化配置 | `pyproject.toml` |
| 类型检查 | `mypy.ini` / `pyrightconfig.json` |
| 测试配置 | `tests/conftest.py` |
| Pre-commit 配置 | `.pre-commit-config.yaml` |
| 构建配置 | `Makefile` |