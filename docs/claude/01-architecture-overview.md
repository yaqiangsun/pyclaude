# Claude Code 总体架构分析

## 一、项目概述

Claude Code 是一个基于 TypeScript 构建的 AI 编程助手 CLI 工具，提供与 Claude AI 模型交互的完整功能。项目使用 React 作为 UI 层，TypeScript 作为主要开发语言，支持多种部署模式（本地、远程、桥接）。

## 二、目录结构概览

```
src/
├── QueryEngine.ts          # 核心查询引擎
├── Task.ts                 # 任务类型定义
├── Tool.ts                 # 工具系统定义
├── commands.ts             # 命令注册和加载
├── query.ts                # 核心查询循环
├── history.ts              # 历史记录管理
├── interactiveHelpers.tsx  # 交互式辅助函数
├── setup.ts                # 初始化设置
├── cost-tracker.ts         # 成本跟踪
│
├── bridge/                 # 远程桥接模块 ⭐
│   ├── bridgeMain.ts
│   ├── bridgeApi.ts
│   ├── replBridge.ts
│   ├── remoteBridgeCore.ts
│   ├── sessionRunner.ts
│   └── ...
│
├── cli/                    # CLI 传输层
│   ├── transports/         # 传输协议实现
│   ├── handlers/           # 命令处理器
│   ├── structuredIO.ts
│   └── remoteIO.ts
│
├── commands/               # 100+ 命令实现
│   ├── commit/
│   ├── config/
│   ├── mcp/
│   └── ...
│
├── hooks/                  # React Hooks (90+)
│   ├── useRemoteSession.ts
│   ├── useSettings.ts
│   └── ...
│
├── services/               # 业务服务层
│   ├── api/                # API 客户端
│   ├── mcp/                # MCP 协议
│   ├── analytics/          # 分析服务
│   └── compact/            # 压缩服务
│
├── state/                  # 状态管理
│   ├── AppStateStore.ts
│   ├── store.ts
│   └── selectors.ts
│
├── components/             # React 组件 (140+)
├── utils/                  # 工具函数 (330+)
├── constants/              # 常量定义
└── types/                  # 类型定义
```

## 三、核心架构层次

### 3.1 分层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   CLI 输入   │  │   UI 界面   │  │  远程桥接   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      命令系统层                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  commands.ts - 命令注册、加载、过滤                   │    │
│  │  commands/  - 100+ 命令实现                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      核心处理层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │QueryEngine  │  │  query.ts   │  │   Tool.ts   │          │
│  │  查询引擎   │  │  查询循环   │  │  工具系统   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      服务层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  API 客户端 │  │ MCP 服务    │  │ 分析服务    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      状态管理层                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  AppState Store + Hooks (useAppState, useSetAppState)│   │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心模块职责

| 模块 | 位置 | 职责 |
|------|------|------|
| **QueryEngine** | `QueryEngine.ts` | 管理对话生命周期、消息历史、工具执行上下文 |
| **query.ts** | `query.ts` | 核心查询循环，与 API 交互，执行工具，处理压缩 |
| **Tool.ts** | `Tool.ts` | 工具接口定义、工具构建器、工具查找 |
| **Task.ts** | `Task.ts` | 任务类型定义（bash/agent/workflow等） |
| **commands.ts** | `commands.ts` | 命令注册、加载、过滤、查找 |
| **history.ts** | `history.ts` | 用户输入历史管理 |
| **bridge/** | `bridge/` | 远程控制桥接实现 |

## 四、核心数据流

### 4.1 主查询流程

```
用户输入
    │
    ▼
commands.ts (命令解析)
    │
    ▼
QueryEngine.submitMessage()
    │
    ▼
query.ts (query 函数)
    │
    ├─▶ API 调用 (流式)
    │       │
    │       ▼
    │   工具调用 (Tool.ts)
    │       │
    │       ▼
    │   执行结果返回
    │
    ▼
消息追加到历史
```

### 4.2 远程桥接流程

```
用户 (claude.ai 网页)
    │
    ▼
Bridge API (环境注册/轮询)
    │
    ▼
bridgeMain.ts / replBridge.ts
    │
    ▼
SessionRunner (子进程管理)
    │
    ▼
本地 CLI 执行命令
    │
    ▼
结果返回给远程
```

## 五、状态管理

### 5.1 AppState 结构

项目使用自定义轻量级 Store，而非 Redux：

```typescript
// store.ts
export type Store<T> = {
  getState: () => T
  setState: (updater: (prev: T) => T) => void
  subscribe: (listener: Listener) => () => void
}
```

### 5.2 全局状态字段（部分）

```typescript
interface AppState {
  // 基础设置
  settings: Settings
  mainLoopModel: string

  // 任务管理
  tasks: Record<string, TaskState>
  foregroundedTaskId: string

  // MCP 和插件
  mcp: { clients: MCPServerConnection[], tools: Tools }
  plugins: { enabled: string[], disabled: string[] }

  // 远程桥接
  replBridgeEnabled: boolean
  replBridgeConnected: boolean

  // 通知
  notifications: { current: Notification[], queue: Notification[] }
}
```

### 5.3 Hook 访问方式

```typescript
// 读取状态
const settings = useAppState(s => s.settings)

// 更新状态
const setAppState = useSetAppState()
setAppState(prev => ({ ...prev, settings: newSettings }))
```

## 六、通信协议

### 6.1 桥接模式

| 模式 | 说明 | 主要文件 |
|------|------|----------|
| **Env-based (v1)** | 基于 Environments API | `bridgeMain.ts` |
| **Env-less (v2)** | 直接连接 Session Ingress | `remoteBridgeCore.ts` |

### 6.2 传输协议

| 传输方式 | 用途 | 文件 |
|----------|------|------|
| WebSocket | 双向实时通信 | `WebSocketTransport.ts` |
| SSE | 服务器推送 | `SSETransport.ts` |
| Hybrid | WebSocket读 + HTTP写 | `HybridTransport.ts` |

### 6.3 API 认证

- OAuth 2.0 (Bearer Token)
- 支持可信设备认证
- 自动 Token 刷新

## 七、工具系统

### 7.1 工具类型

```typescript
type Tool = {
  name: string              // 工具名称
  inputSchema: ZodSchema    // 输入参数 Schema
  description(): string     // 描述生成

  // 执行方法
  call(args, context, canUseTool, parentMessage, onProgress): Promise<ToolResult>

  // 能力定义
  isConcurrencySafe(): boolean
  isReadOnly(): boolean
  isDestructive(): boolean

  // 权限检查
  checkPermissions(): Promise<PermissionResult>
}
```

### 7.2 工具来源

1. **内置工具**: `src/tools/` 目录（约40+）
2. **MCP 工具**: 通过 MCP 协议加载
3. **插件工具**: 通过插件系统加载

### 7.3 工具执行流程

```
LLM 决定使用工具
    │
    ▼
canUseTool 检查权限
    │
    ▼
Tool.call() 执行
    │
    ├─▶ 权限请求 (elicitation)
    │       │
    │       ▼
    │   用户授权/拒绝
    │
    ▼
返回 ToolResult
```

## 八、命令系统

### 8.1 命令类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `prompt` | 返回提示供模型执行 | `/commit` |
| `local` | 本地同步执行 | `/clear` |
| `local-jsx` | 需要渲染 UI | `/config` |

### 8.2 命令来源

- `builtin`: 内置命令
- `mcp`: MCP 服务器
- `plugin`: 插件
- `bundled`: 捆绑技能
- `skills`: 用户技能

### 8.3 命令执行

```typescript
// 命令查找
const cmd = findCommand('/commit', commands)

// 本地命令直接执行
if (cmd.type === 'local') {
  const handler = await cmd.load()
  await handler.default(args)
}

// Prompt 命令返回内容
if (cmd.type === 'prompt') {
  const prompt = await cmd.getPromptForCommand(args, context)
  // 追加到消息中
}
```

## 九、关键设计模式

### 9.1 观察者模式

- **Store**: 状态订阅机制
- **EventEmitter**: 事件驱动通信

### 9.2 工厂模式

- **buildTool()**: 工具构建器，应用默认配置
- **Transport 工厂**: 根据 URL 选择传输实现

### 9.3 策略模式

- **工具能力**: `isConcurrencySafe`, `isReadOnly`, `isDestructive`
- **认证策略**: Direct API、AWS Bedrock、Azure Foundry、Vertex AI

### 9.4 装饰器模式

- **withRetry()**: API 重试装饰器
- **消息装饰**: 追加系统提示、上下文

### 9.5 懒加载模式

- **命令加载**: `load()` 方法延迟加载
- **Hook 加载**: `useRemoteSession` 等按需加载

## 十、技术栈

| 类别 | 技术 |
|------|------|
| 语言 | TypeScript |
| UI | React |
| 状态 | 自定义 Store (非 Redux) |
| API | Anthropic SDK |
| 协议 | MCP (Model Context Protocol) |
| 构建 | 待确认 (可能是 tsup/Vite) |
| 测试 | 待确认 |

## 十一、后续开发建议

基于本分析，为 Python 版本（claudex）开发建议：

1. **保持分层架构**: 清晰分离 CLI、核心引擎、服务层
2. **实现核心类型**: 首先实现 `Tool`, `Task`, `QueryEngine` 的 Python 版本
3. **桥接模块独立**: Bridge 模块可作为独立包
4. **状态管理简化**: 使用简单的观察者模式或参考 Python 惯用方式
5. **传输层抽象**: 定义Transport 接口，支持多种协议
6. **命令系统可扩展**: 保持命令注册机制，支持插件化

---

*文档版本: 1.0*
*分析时间: 2026-04-08*