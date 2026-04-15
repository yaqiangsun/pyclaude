# Claude Code Python 版本设计文档

## 文档索引

本文档采用总分结构，先总体设计，再分模块设计。

### 总体设计
- [01-总览与架构设计](./01-overview.md) - 项目目标、技术选型、整体架构

### 核心模块设计
- [02-核心引擎模块](./02-core-engine.md) - QueryEngine、Task、Tool 核心系统
- [03-命令系统](./03-commands.md) - 命令注册、加载、执行
- [04-工具系统](./04-tools.md) - 45+ 内置工具、权限系统
- [05-查询循环](./05-query-loop.md) - API 交互、上下文压缩

### 通信与传输
- [06-Bridge 远程桥接](./06-bridge.md) - claude.ai 远程控制
- [07-传输层](./07-transports.md) - WebSocket、SSE、Hybrid

### 服务层
- [08-服务层](./08-services.md) - API 客户端、MCP、Analytics
- [09-技能系统](./09-skills.md) - 15+ 内置技能、动态发现

### UI 与交互
- [10-CLI 界面](./10-cli-ui.md) - Ink 框架替代方案
- [11-输入系统](./11-input-system.md) - 快捷键、Vim 模式
- [12-状态管理](./12-state-management.md) - Store、状态管理

### 基础设施
- [13-工具库](./13-utils.md) - 330+ 工具函数
- [14-常量定义](./14-constants.md) - API 限制、提示词
- [15-启动流程](./15-startup.md) - 初始化流程
- [16-其他模块](./16-additional.md) - Buddy、Coordinator、Memdir

### 开发规范
- [17-代码规范](./17-coding-standards.md) - 项目结构、代码风格、测试规范、示例代码

## 与 TypeScript 版本对应关系

| TypeScript | Python 实现 |
|------------|-------------|
| QueryEngine.ts | `pyclaude/engine.py` |
| Tool.ts | `pyclaude/tools/base.py` (Protocol/ABC) |
| Task.ts | `pyclaude/core/task.py` (Enum) |
| query.ts | `pyclaude/core/query.py` |
| history.ts | `pyclaude/core/history.py` |
| commands.ts | `pyclaude/commands/__init__.py` |
| setup.ts | `pyclaude/setup.py` |
| bridge/ | `pyclaude/bridge/` |
| cli/ | `pyclaude/cli/` |
| commands/ | `pyclaude/commands/` |
| hooks/ | `pyclaude/hooks/` |
| services/ | `pyclaude/services/` |
| tools/ | `pyclaude/tools/` |
| skills/ | `pyclaude/skills/` |
| state/ | `pyclaude/state/` |
| utils/ | `pyclaude/utils/` |
| constants/ | `pyclaude/constants/` |