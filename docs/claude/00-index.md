# Claude Code 架构分析文档

本文档是 Claude Code TypeScript 源代码的完整架构分析索引，提供对项目整体结构和各模块的深入理解。

---

## 文档结构

```
docs/claude/
├── 00-index.md          # 本文档 - 总索引
├── 01-architecture-overview.md  # 总体架构分析
├── 02-core-modules.md   # 核心模块分析
├── 03-bridge-module.md  # Bridge 桥接模块
├── 04-cli-commands.md   # CLI 和命令系统
└── 05-hooks-services.md # Hooks 和 Services
```

---

## 快速导航

### 第一层：总体架构

📄 **[01-architecture-overview.md](01-architecture-overview.md)**

- 项目概述和目录结构
- 分层架构设计（用户交互层 → 命令系统层 → 核心处理层 → 服务层 → 状态管理层）
- 核心数据流（主查询流程、远程桥接流程）
- 状态管理机制（AppState、Store）
- 通信协议（桥接模式、传输协议、API 认证）
- 工具系统和命令系统概述
- 关键设计模式（观察者、工厂、策略、装饰器、懒加载）
- 技术栈说明

---

### 第二层：核心模块

📄 **[02-core-modules.md](02-core-modules.md)**

#### 1. QueryEngine.ts - 核心查询引擎
- `QueryEngine` 类设计
- `QueryEngineConfig` 配置结构
- `submitMessage()` 异步生成器
- `ask()` 便捷函数

#### 2. Task.ts - 任务定义
- `TaskType` 任务类型（local_bash, local_agent, remote_agent 等）
- `TaskStatus` 任务状态（pending, running, completed 等）
- `generateTaskId()` ID 生成算法
- 任务上下文定义

#### 3. Tool.ts - 工具系统
- `Tool<T>` 泛型接口定义
- 工具能力（isConcurrencySafe, isReadOnly, isDestructive 等）
- 权限检查机制
- 渲染和 UI 方法
- `buildTool()` 工具构建器

#### 4. commands.ts - 命令系统
- 命令类型（prompt, local, local-jsx）
- 命令注册和加载机制
- 命令查找和过滤
- 常用命令示例

#### 5. query.ts - 核心查询循环
- `QueryParams` 查询参数
- `query()` 主查询函数
- 预处理、API 调用、工具执行、后处理流程
- 上下文压缩流程（snip, microcompact, collapse, autocompact）
- 错误恢复机制
- 性能优化策略

#### 6. history.ts - 历史记录
- 历史数据类型
- 添加/获取历史记录
- 粘贴内容处理
- 存储机制（JSONL 格式）

---

### 第三层：桥接模块

📄 **[03-bridge-module.md](03-bridge-module.md)**

- 两种桥接模式（Env-based v1 vs Env-less v2）
- Bridge API 客户端接口
- 会话创建和管理（`SessionHandle`）
- 消息格式和传递（SDK 消息类型、控制请求）
- 传输层（HybridTransport, SSETransport）
- 配置和初始化流程
- JWT 和 Token 管理
- Work Secret 协议
- 错误处理机制

---

### 第四层：CLI 和命令

📄 **[04-cli-commands.md](04-cli-commands.md)**

#### 命令系统
- 命令类型定义（PromptCommand, LocalCommand, LocalJSXCommand）
- 命令执行流程
- 命令注册机制
- 常用命令示例

#### 传输层
- `Transport` 接口定义
- WebSocket 传输实现
- SSE 传输实现
- Hybrid 传输实现
- 传输选择逻辑

#### 输入输出
- `StructuredIO` 结构化输入输出
- `RemoteIO` 远程输入输出
- NDJSON 处理
- 打印和输出

---

### 第五层：Hooks 和 Services

📄 **[05-hooks-services.md](05-hooks-services.md)**

#### Hooks 模块（90+ 个）
- 状态管理 Hooks（useAppState, useSetAppState, useSettings）
- 输入处理 Hooks（useTextInput, useVimInput）
- 远程连接 Hooks（useRemoteSession）
- 工具和插件 Hooks（useMergedTools, useManageMCPConnections）
- 通知系统 Hooks（10+ 个通知类型）

#### Services 模块（50+ 个）
- API 客户端（Anthropic, AWS Bedrock, Azure Foundry, Vertex AI）
- MCP 协议实现
- 分析服务（事件日志、特性开关）
- 压缩服务（snip, microcompact, collapse, autocompact）
- OAuth、插件、LSP 服务

#### 状态管理
- 自定义 Store 实现（观察者模式）
- AppState 数据结构
- 选择器函数
- 组件间通信方式

---

## 模块依赖关系图

```
┌──────────────────────────────────────────────────────────────────┐
│                         用户交互层                                │
│   CLI 输入  │  UI 界面  │  远程桥接                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      04-cli-commands.md                          │
│              CLI 传输层 + 命令系统                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      02-core-modules.md                          │
│  QueryEngine  │  query.ts  │  Tool.ts  │  Task.ts  │  history.ts │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      03-bridge-module.md                         │
│                    远程桥接模块                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      05-hooks-services.md                        │
│              Hooks (90+)  │  Services (50+)  │  State            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 核心类型映射（供 Python 实现参考）

| TypeScript | 位置 | Python 建议实现 |
|------------|------|-----------------|
| `QueryEngine` | 02-core-modules.md | `class QueryEngine` |
| `QueryEngineConfig` | 02-core-modules.md | `@dataclass` |
| `Tool` | 02-core-modules.md | `Protocol` |
| `TaskType` | 02-core-modules.md | `Enum` |
| `Message` | 02-core-modules.md | `dataclass` |
| `BridgeApiClient` | 03-bridge-module.md | `class` |
| `SessionHandle` | 03-bridge-module.md | `class` |
| `Transport` | 04-cli-commands.md | `Protocol` |
| `Command` | 04-cli-commands.md | `Protocol` |
| `Store<T>` | 05-hooks-services.md | `Generic[T]` |
| `AppState` | 05-hooks-services.md | `@dataclass` |

---

## 建议阅读顺序

1. **初学者**: 01 → 02 → 03 → 04 → 05
2. **有经验者**: 直接查看感兴趣的部分
3. **Python 实现**: 重点参考 02-core-modules.md 和模块依赖关系

---

## 相关资源

- 源代码: `/src/`
- 桥接模块: `/src/bridge/`
- CLI 模块: `/src/cli/`
- Hooks: `/src/hooks/`
- Services: `/src/services/`

---

*文档版本: 1.0*
*最后更新: 2026-04-08*