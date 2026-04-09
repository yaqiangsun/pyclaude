# CLI 和命令系统分析

本文档详细分析 Claude Code 的 CLI 传输层和命令系统的架构设计。

---

## 一、CLI 模块概述

### 1.1 目录结构

```
src/cli/
├── handlers/                    # 命令处理器
│   ├── auth.ts
│   ├── agents.ts
│   ├── mcp.tsx
│   ├── plugins.ts
│   ├── autoMode.ts
│   └── util.tsx
├── transports/                  # 传输协议实现
│   ├── HybridTransport.ts
│   ├── SSETransport.ts
│   ├── WebSocketTransport.ts
│   ├── SerialBatchEventUploader.ts
│   ├── WorkerStateUploader.ts
│   ├── ccrClient.ts
│   └── transportUtils.ts
├── structuredIO.ts              # 结构化输入输出
├── remoteIO.ts                  # 远程 I/O
├── print.ts                     # 打印输出
├── exit.ts                      # 退出处理
├── update.ts                    # 更新处理
├── remoteIO.ts
└── ndjsonSafeStringify.ts       # NDJSON 工具
```

### 1.2 主要职责

- 命令行输入输出处理
- 多种传输协议支持
- 与远程服务端通信
- 消息编解码

---

## 二、命令注册和执行机制

### 2.1 命令类型定义 (types/command.ts)

```typescript
// Prompt 类型命令 - 返回提示供模型执行
type PromptCommand = {
  type: 'prompt'
  name: string
  description: string
  aliases?: string[]
  allowedTools?: string[]
  contentLength?: number
  source: 'builtin' | 'mcp' | 'plugin' | 'bundled' | 'skills'
  getPromptForCommand(
    args: string,
    context: GetPromptForCommandContext
  ): Promise<PromptContent[]>
  whenToUse?: string
  hasUserSpecifiedDescription?: boolean
  disableModelInvocation?: boolean
  loadedFrom?: string
}

// 本地命令 - 同步执行
type LocalCommand = {
  type: 'local'
  name: string
  description: string
  aliases?: string[]
  load: () => Promise<CommandModule>
  requires?: string[]
}

// 本地 JSX 命令 - 需要渲染 UI
type LocalJSXCommand = {
  type: 'local-jsx'
  name: string
  description: string
  aliases?: string[]
  load: () => Promise<CommandModule>
}
```

### 2.2 命令执行流程

```
用户输入 (/command args)
    │
    ▼
命令解析 (commands.ts)
    │
    ├─▶ type === 'prompt'
    │       │
    │       ▼
    │   getPromptForCommand(args, context)
    │       │
    │       ▼
    │   追加到消息中供模型执行
    │
    ├─▶ type === 'local'
    │       │
    │       ▼
    │   load() → 加载模块
    │       │
    │       ▼
    │   执行 handler.default(args)
    │
    └─▶ type === 'local-jsx'
            │
            ▼
        load() → 加载 React 组件
            │
            ▼
        渲染 UI
```

### 2.3 命令注册机制 (commands.ts)

```typescript
// 命令缓存
const COMMANDS = memoize((): Command[] => [
  addDir,
  advisor,
  autofixPr,
  backfillSessions,
  // ... 100+ commands
])

// 获取所有命令
export async function getCommands(cwd: string): Promise<Command[]> {
  const allCommands = await loadAllCommands(cwd)
  const dynamicSkills = getDynamicSkills()
  const baseCommands = allCommands.filter(
    _ => meetsAvailabilityRequirement(_) && isCommandEnabled(_),
  )
  // 去重动态技能
  // ...
  return [...baseCommands.slice(insertIndex), ...uniqueDynamicSkills, ...baseCommands.slice(insertIndex)]
}

// 技能工具命令
export const getSkillToolCommands = memoize(
  async (cwd: string): Promise<Command[]> => {
    const allCommands = await getCommands(cwd)
    return allCommands.filter(
      cmd =>
        cmd.type === 'prompt' &&
        !cmd.disableModelInvocation &&
        cmd.source !== 'builtin' &&
        (cmd.loadedFrom === 'bundled' ||
          cmd.loadedFrom === 'skills' ||
          cmd.loadedFrom === 'commands_DEPRECATED' ||
          cmd.hasUserSpecifiedDescription ||
          cmd.whenToUse),
    )
  },
)

// 斜杠命令技能
export const getSlashCommandToolSkills = memoize(
  async (cwd: string): Promise<Command[]> => {
    // 过滤：type === 'prompt', 非 builtin, 有描述或 whenToUse
  },
)
```

### 2.4 命令查找

```typescript
// 查找命令
export function findCommand(commandName: string, commands: Command[]): Command | undefined

// 判断是否有命令
export function hasCommand(commandName: string, commands: Command[]): boolean

// 获取命令
export function getCommand(commandName: string, commands: Command[]): Command
```

### 2.5 常用命令示例

| 命令 | 类型 | 功能 | 文件 |
|------|------|------|------|
| `/commit` | prompt | 创建 git 提交 | `commands/commit.ts` |
| `/config` | local-jsx | 打开配置面板 | `commands/config/index.ts` |
| `/help` | local-jsx | 显示帮助 | `commands/help/index.ts` |
| `/mcp` | local-jsx | MCP 服务器管理 | `commands/mcp/index.ts` |
| `/clear` | local | 清除对话 | `commands/clear/index.ts` |
| `/resume` | local-jsx | 恢复会话 | `commands/resume/index.ts` |
| `/diff` | local-jsx | 查看变更 | `commands/diff/index.ts` |
| `/doctor` | local | 诊断问题 | `commands/doctor/index.ts` |

---

## 三、传输层设计

### 3.1 Transport 接口

```typescript
interface Transport {
  // 读取
  read(): AsyncGenerator<Message, void, unknown>

  // 写入
  write(message: Message): Promise<void>

  // 关闭
  close(): Promise<void>

  // 状态
  get isConnected(): boolean
}
```

### 3.2 WebSocket 传输 (WebSocketTransport.ts)

```typescript
export class WebSocketTransport implements Transport {
  private ws: WebSocket
  private messageQueue: Message[] = []

  constructor(
    private url: string,
    private headers: Record<string, string>,
    private sessionId: string,
    private refreshHeaders?: () => Promise<Record<string, string>>
  ) {}

  async *read(): AsyncGenerator<Message> {
    // 1. 建立 WebSocket 连接
    // 2. 处理消息
    // 3. 自动重连（指数退避）
  }

  async write(message: Message): Promise<void> {
    // 发送消息到 WebSocket
  }
}
```

**特点**:
- 双向实时通信
- 自动重连机制（指数退避）
- 支持 Bun 原生 WebSocket 和 ws 包
- 心跳检测和代理支持

### 3.3 SSE 传输 (SSETransport.ts)

```typescript
export class SSETransport implements Transport {
  constructor(
    private url: string,
    private headers: Record<string, string>,
    private sessionId: string,
    private refreshHeaders?: () => Promise<Record<string, string>>
  ) {}

  async *read(): AsyncGenerator<Message> {
    // 1. 建立 SSE 连接
    // 2. 处理 event: message
    // 3. Last-Event-ID 支持断点续传
  }

  async write(message: Message): Promise<void> {
    // HTTP POST 写入
  }
}
```

**特点**:
- SSE (Server-Sent Events) 读取
- HTTP POST 写入
- 用于 CCR v2 事件流
- Last-Event-ID 支持断点续传

### 3.4 Hybrid 传输 (HybridTransport.ts)

```typescript
export class HybridTransport implements Transport {
  constructor(
    private url: URL,
    private headers: Record<string, string>,
    private sessionId: string,
    private refreshHeaders?: () => Promise<Record<string, string>>
  ) {}

  async *read(): AsyncGenerator<Message> {
    // WebSocket 读取
  }

  async write(message: Message): Promise<void> {
    // 使用 SerialBatchEventUploader 批量写入
  }
}
```

**特点**:
- WebSocket 读取 + HTTP POST 写入
- 使用 `SerialBatchEventUploader` 进行批量写入
- 串行化请求避免 Firestore 冲突

### 3.5 传输选择 (transportUtils.ts)

```typescript
export function getTransportForUrl(
  url: URL,
  headers: Record<string, string>,
  sessionId: string,
  refreshHeaders?: () => Promise<Record<string, string>>
): Transport {
  if (isEnvTruthy(process.env.CLAUDE_CODE_USE_CCR_V2)) {
    return new SSETransport(sseUrl, headers, sessionId, refreshHeaders)
  }

  if (url.protocol === 'ws:' || url.protocol === 'wss:') {
    if (isEnvTruthy(process.env.CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2)) {
      return new HybridTransport(url, headers, sessionId, refreshHeaders)
    }
    return new WebSocketTransport(url, headers, sessionId, refreshHeaders)
  }
}
```

---

## 四、StructuredIO 和 RemoteIO

### 4.1 StructuredIO (structuredIO.ts)

核心类处理 SDK 协议的 stdin/stdout 通信：

```typescript
export class StructuredIO {
  readonly structuredInput: AsyncGenerator<StdinMessage | SDKMessage>
  private readonly pendingRequests = new Map<string, PendingRequest<unknown>>()

  constructor(
    input: AsyncIterable<string>,
    options: StructuredIOOptions = {}
  ) {
    this.structuredInput = this.parseInput(input)
  }

  // 处理控制请求
  async handleControlRequest(request: SDKControlRequest): Promise<SDKControlResponse> {
    // 根据 request.subtype 处理
    // initialize, set_model, set_permission_mode, interrupt, can_use_tool
  }

  // 处理权限请求
  async handlePermissionRequest(tool: Tool, input: Record<string, unknown>): Promise<void> {
    // 发送权限请求
    // 等待用户响应
    // 返回授权/拒绝
  }

  // 处理用户中断
  handleInputCancellation(): void {
    // 处理 Ctrl+C 中断
  }
}
```

### 4.2 RemoteIO (remoteIO.ts)

继承 `StructuredIO`，包装传输层：

```typescript
export class RemoteIO extends StructuredIO {
  private transport: Transport
  private ccrClient: CCRClient | null = null

  constructor(
    streamUrl: string,
    initialPrompt?: AsyncIterable<string>,
    replayUserMessages?: boolean
  ) {
    // 初始化传输层
    this.transport = getTransportForUrl(
      new URL(streamUrl),
      this.getDefaultHeaders(),
      getSessionId(),
      this.refreshHeaders
    )
    super(this.transport.read(), { replayUserMessages })
  }

  // 发送消息
  async sendMessage(message: SDKMessage): Promise<void> {
    await this.transport.write(message)
  }

  // 关闭连接
  async close(): Promise<void> {
    await this.transport.close()
  }
}
```

---

## 五、命令处理器

### 5.1 handlers 目录结构

```
src/cli/handlers/
├── auth.ts           # 认证处理
├── agents.ts         # Agent 管理
├── mcp.tsx           # MCP 服务器管理
├── plugins.ts        # 插件安装/卸载
├── autoMode.ts       # 自动模式处理
└── util.tsx          # 实用工具处理（doctor, install 等）
```

### 5.2 主要处理器

#### MCP 处理器 (mcp.tsx)

```typescript
export async function handleMcpCommand(args: string[]): Promise<void> {
  // mcp list - 列出服务器
  // mcp add <name> <command> - 添加服务器
  // mcp remove <name> - 移除服务器
  // mcp start <name> - 启动服务器
  // mcp stop <name> - 停止服务器
}
```

#### 插件处理器 (plugins.ts)

```typescript
export async function handlePluginCommand(args: string[]): Promise<void> {
  // plugin list - 列出插件
  // plugin install <name> - 安装插件
  // plugin uninstall <name> - 卸载插件
  // plugin enable <name> - 启用插件
  // plugin disable <name> - 禁用插件
}
```

---

## 六、输入输出处理

### 6.1 消息格式

```typescript
// 标准消息格式
type Message = {
  type: 'user' | 'assistant' | 'system' | 'tool_use' | 'tool_result'
  content: string | ContentBlock[]
  role?: 'user' | 'assistant'
  [key: string]: unknown
}

// SDK 消息格式
type SDKMessage = {
  type: string
  request_id?: string
  message: Message
  [key: string]: unknown
}
```

### 6.2 NDJSON 处理 (ndjsonSafeStringify.ts)

```typescript
// 安全序列化 NDJSON
export function ndjsonSafeStringify(obj: object): string {
  const json = JSON.stringify(obj)
  if (json.includes('\n')) {
    throw new Error('NDJSON must not contain newlines')
  }
  return json + '\n'
}

// 安全解析 NDJSON
export function ndjsonSafeParse(line: string): object {
  return JSON.parse(line)
}
```

---

## 七、打印和输出

### 7.1 print.ts

```typescript
// 打印类型
type PrintType = 'info' | 'warn' | 'error' | 'success' | 'progress' | 'spinner'

// 打印函数
export function print(message: string, type: PrintType = 'info'): void {
  // 根据类型使用不同的样式
}

// 进度打印
export function printProgress(message: string, progress: number): void {
  // 显示进度条
}

//  spinner
export function createSpinner(message: string): Spinner {
  return {
    start: () => {},
    stop: () => {},
    update: (message: string) => {},
  }
}
```

---

## 八、关键设计模式

### 8.1 工厂模式

```typescript
// 传输层工厂
const transportFactory = {
  create(config: TransportConfig): Transport {
    switch (config.type) {
      case 'websocket':
        return new WebSocketTransport(config)
      case 'sse':
        return new SSETransport(config)
      case 'hybrid':
        return new HybridTransport(config)
      default:
        throw new Error(`Unknown transport type: ${config.type}`)
    }
  }
}
```

### 8.2 策略模式

```typescript
// 认证策略
interface AuthStrategy {
  authenticate(): Promise<string>
}

// Direct API 认证
class DirectApiAuth implements AuthStrategy {
  async authenticate(): Promise<string> {
    return getApiKey()
  }
}

// OAuth 认证
class OAuthAuth implements AuthStrategy {
  async authenticate(): Promise<string> {
    return getOAuthToken()
  }
}
```

### 8.3 观察者模式

```typescript
// StructuredIO 消息订阅
class MessageSubject {
  private observers: Set<Observer> = new Set()

  subscribe(observer: Observer): () => void {
    this.observers.add(observer)
    return () => this.observers.delete(observer)
  }

  notify(message: Message): void {
    for (const observer of this.observers) {
      observer.onMessage(message)
    }
  }
}
```

---

## 九、Python 版本实现建议

### 9.1 模块映射

| TypeScript | Python | 说明 |
|------------|--------|------|
| `Transport` | `Protocol Transport` | 传输层抽象 |
| `WebSocketTransport` | `class WebSocketTransport` | WebSocket 传输 |
| `SSETransport` | `class SSETransport` | SSE 传输 |
| `HybridTransport` | `class HybridTransport` | 混合传输 |
| `StructuredIO` | `class StructuredIO` | 结构化 I/O |
| `RemoteIO` | `class RemoteIO` | 远程 I/O |
| `Command` | `Protocol Command` | 命令接口 |
| `commands.ts` | `commands/registry.py` | 命令注册 |

### 9.2 建议的包结构

```
cludex/cli/
├── __init__.py
├── commands/
│   ├── __init__.py
│   ├── registry.py      # 命令注册表
│   ├── finder.py        # 命令查找
│   └── builtins/        # 内置命令
│       ├── __init__.py
│       ├── commit.py
│       ├── config.py
│       └── ...
├── transport/
│   ├── __init__.py
│   ├── base.py          # Transport 抽象基类
│   ├── websocket.py     # WebSocket 传输
│   ├── sse.py           # SSE 传输
│   └── hybrid.py        # Hybrid 传输
├── io/
│   ├── __init__.py
│   ├── structured.py    # StructuredIO
│   ├── remote.py        # RemoteIO
│   └── print.py         # 打印工具
└── handlers/
    ├── __init__.py
    ├── auth.py
    ├── mcp.py
    └── plugins.py
```

### 9.3 关键实现要点

1. **异步生成器**: 保持 `async for` 流式处理模式
2. **传输抽象**: 使用 Protocol 定义传输接口
3. **命令系统**: 保持可扩展性，支持插件
4. **类型安全**: 使用 dataclass 和 Protocol
5. **错误处理**: 实现重试和退避机制

---

*文档版本: 1.0*
*分析时间: 2026-04-08*