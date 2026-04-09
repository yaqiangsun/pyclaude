# Hooks 和 Services 分析

本文档详细分析 Claude Code 的 React Hooks 模块和 Services 服务层。

---

## 一、Hooks 目录概述

### 1.1 目录结构

```
src/hooks/
├── useAppState.ts              # 访问全局状态
├── useSetAppState.ts           # 更新全局状态
├── useSettings.ts              # 用户设置
├── useMainLoopModel.ts         # 主循环模型
├── useTasksV2.ts               # 任务列表管理
├── useCommandQueue.ts          # 命令队列
├── useTextInput.ts             # 文本输入
├── useSearchInput.ts           # 搜索输入
├── useRemoteSession.ts         # 远程会话管理
├── useMergedTools.ts           # 合并工具列表
├── useMergedCommands.ts        # 合并命令列表
├── useManagePlugins.ts         # 插件管理
├── useManageMCPConnections.ts  # MCP 连接管理
│
├── notifs/                     # 通知系统
│   ├── useStartupNotification.ts
│   ├── useModelMigrationNotifications.ts
│   ├── usePluginInstallationStatus.ts
│   └── ...
│
└── [90+ 其他 hooks]
```

### 1.2 Hook 分类

| 类别 | 数量 | 功能 |
|------|------|------|
| 状态管理 | ~20 | 全局状态访问和更新 |
| 输入处理 | ~15 | 文本、搜索、Vim 输入 |
| 远程连接 | ~10 | WebSocket、SSH、IDE 连接 |
| 工具和插件 | ~15 | MCP、插件、工具管理 |
| 通知系统 | ~10 | 各类用户通知 |
| 实用工具 | ~20 | 计时器、超时、虚拟滚动等 |

---

## 二、核心 Hooks 详解

### 2.1 状态管理 Hooks

#### useAppState - 读取全局状态

```typescript
// 使用选择器读取状态
export function useAppState<T>(selector: (state: AppState) => T): T {
  const store = useContext(AppStateContext)
  return useSyncExternalStore(
    store.subscribe,
    () => selector(store.getState()),
    () => selector(INITIAL_APP_STATE)
  )
}

// 使用示例
const settings = useAppState(s => s.settings)
const tasks = useAppState(s => s.tasks)
const foregroundedTaskId = useAppState(s => s.foregroundedTaskId)
```

#### useSetAppState - 更新全局状态

```typescript
export function useSetAppState(): (updater: (prev: AppState) => AppState) => void {
  const store = useContext(AppStateContext)
  return store.setState
}

// 使用示例
const setAppState = useSetAppState()
setAppState(prev => ({
  ...prev,
  settings: { ...prev.settings, theme: 'dark' }
}))
```

#### useSettings - 用户设置

```typescript
export function useSettings(): Settings {
  const settings = useAppState(s => s.settings)

  // 监听文件变化，自动重新加载
  useEffect(() => {
    const watcher = watchFile(settingsPath, () => {
      reloadSettings()
    })
    return () => watcher.close()
  }, [])

  return settings
}
```

### 2.2 输入处理 Hooks

#### useTextInput - 文本输入

```typescript
export function useTextInput(options: TextInputOptions = {}) {
  const [value, setValue] = useState('')
  const [history, setHistory] = useState<string[]>([])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      setHistory(prev => [...prev, value])
      options.onSubmit?.(value)
      setValue('')
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      // 上一条历史
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      // 下一条历史
    }
  }

  return { value, setValue, handleChange, handleKeyDown, history }
}
```

#### useVimInput - Vim 模式输入

```typescript
export function useVimInput() {
  const [mode, setMode] = useState<'normal' | 'insert' | 'visual'>('normal')

  const handleKeyDown = (e: KeyboardEvent) => {
    switch (mode) {
      case 'normal':
        if (e.key === 'i') setMode('insert')
        if (e.key === 'v') setMode('visual')
        if (e.key === ':') handleCommand()
        break
      case 'insert':
        if (e.key === 'Escape') setMode('normal')
        break
      case 'visual':
        if (e.key === 'Escape') setMode('normal')
        break
    }
  }

  return { mode, setMode, handleKeyDown }
}
```

### 2.3 远程连接 Hooks

#### useRemoteSession - 远程会话管理

```typescript
export function useRemoteSession() {
  const [sessionState, setSessionState] = useState<SessionState>('disconnected')
  const [messages, setMessages] = useState<SDKMessage[]>([])

  // WebSocket 连接
  const connect = useCallback(async (sessionId: string) => {
    setSessionState('connecting')
    const ws = new WebSocket(sessionUrl)

    ws.onopen = () => setSessionState('connected')
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      setMessages(prev => [...prev, message])
    }
    ws.onclose = () => setSessionState('disconnected')
    ws.onerror = () => setSessionState('error')
  }, [])

  // 发送消息
  const send = useCallback(async (message: SDKMessage) => {
    await ws.send(JSON.stringify(message))
  }, [])

  // 断开连接
  const disconnect = useCallback(() => {
    ws.close()
  }, [])

  return { sessionState, messages, connect, send, disconnect }
}
```

### 2.4 工具和插件 Hooks

#### useMergedTools - 合并工具列表

```typescript
export function useMergedTools(initialTools: Tools, toolPermissionContext?: ToolPermissionContext): Tools {
  const mcpTools = useAppState(s => s.mcp.tools)
  const settings = useAppState(s => s.settings)

  return useMemo(() => {
    // 1. 组合内置工具和 MCP 工具
    const allTools = [...initialTools, ...mcpTools]

    // 2. 应用权限过滤
    const filteredTools = applyToolPermissions(allTools, toolPermissionContext, settings)

    // 3. 去除重复
    return deduplicateTools(filteredTools)
  }, [initialTools, mcpTools, toolPermissionContext, settings])
}
```

#### useManageMCPConnections - MCP 连接管理

```typescript
export function useManageMCPConnections() {
  const [connections, setConnections] = useState<MCPConnection[]>([])
  const [loading, setLoading] = useState(false)

  // 启动连接
  const startConnection = useCallback(async (config: MCPConfig) => {
    setLoading(true)
    try {
      const client = await MCPClient.create(config)
      const connection = await client.connect()
      setConnections(prev => [...prev, connection])
      return connection
    } finally {
      setLoading(false)
    }
  }, [])

  // 停止连接
  const stopConnection = useCallback(async (serverName: string) => {
    const connection = connections.find(c => c.name === serverName)
    await connection?.disconnect()
    setConnections(prev => prev.filter(c => c.name !== serverName))
  }, [connections])

  // 重启连接
  const restartConnection = useCallback(async (serverName: string) => {
    await stopConnection(serverName)
    const config = connections.find(c => c.name === serverName)?.config
    if (config) await startConnection(config)
  }, [connections, startConnection, stopConnection])

  return { connections, loading, startConnection, stopConnection, restartConnection }
}
```

### 2.5 通知系统 Hooks

#### notifs 子目录

```
src/hooks/notifs/
├── useStartupNotification.ts           # 启动通知
├── useModelMigrationNotifications.ts   # 模型迁移通知
├── usePluginInstallationStatus.ts      # 插件安装状态
├── usePluginAutoupdateNotification.ts  # 插件自动更新
├── useLspInitializationNotification.ts # LSP 初始化
├── useTeammateShutdownNotification.ts  # 队友关闭通知
├── useAutoModeUnavailableNotification.ts # 自动模式不可用
├── useRateLimitWarningNotification.ts  # 速率限制警告
├── useFastModeNotification.ts          # 快速模式通知
├── useSettingsErrors.ts                # 设置错误
└── useMcpConnectivityStatus.ts         # MCP 连接状态
```

#### 通知创建示例

```typescript
export function useStartupNotification() {
  const addNotification = useAddNotification()

  useEffect(() => {
    // 检查并显示启动通知
    if (shouldShowWelcome()) {
      addNotification({
        type: 'info',
        title: 'Welcome to Claude Code',
        message: 'Get started by typing a message...',
        actions: [
          { label: 'Documentation', action: 'openDocs' },
          { label: 'Dismiss', action: 'dismiss' }
        ]
      })
    }
  }, [])
}
```

---

## 二、Services 目录概述

### 2.1 目录结构

```
src/services/
├── api/                       # API 客户端
│   ├── client.ts              # Anthropic API 客户端
│   ├── claude.ts              # Claude API 封装
│   ├── bootstrap.ts           # 引导请求
│   ├── usage.ts               # 使用量统计
│   ├── errors.ts              # 错误处理
│   ├── withRetry.ts           # 重试逻辑
│   ├── adminRequests.ts       # 管理请求
│   └── filesApi.ts            # 文件 API
│
├── mcp/                       # MCP 协议实现
│   ├── client.ts              # MCP 客户端
│   ├── types.ts               # MCP 类型
│   ├── config.ts              # MCP 配置
│   ├── auth.ts                # MCP 认证
│   ├── channelPermissions.ts  # 渠道权限
│   └── elicitationHandler.ts  # 请求处理
│
├── analytics/                 # 分析服务
│   ├── index.ts               # 主入口
│   ├── sink.ts                # 事件接收器
│   ├── datadog.ts             # Datadog 集成
│   └── growthbook.ts          # GrowthBook 特性开关
│
├── compact/                   # 压缩服务
│   ├── compact.ts             # 主压缩逻辑
│   ├── microCompact.ts        # 微型压缩
│   ├── autoCompact.ts         # 自动压缩
│   └── postCompactCleanup.ts  # 压缩后清理
│
├── PromptSuggestion/          # Prompt 建议
│   ├── promptSuggestion.ts
│   └── speculation.ts
│
├── SessionMemory/             # 会话记忆
│   ├── sessionMemory.ts
│   └── sessionMemoryUtils.ts
│
├── notifier.ts                # 通知服务
├── awaySummary.ts             # 离开摘要
├── oauth/                     # OAuth 服务
├── plugins/                   # 插件操作
└── lsp/                       # LSP 服务
```

### 2.2 服务分类

| 类别 | 数量 | 功能 |
|------|------|------|
| API 客户端 | ~10 | Anthropic API 封装 |
| MCP 协议 | ~8 | Model Context Protocol |
| 分析服务 | ~5 | 事件日志、特性开关 |
| 压缩服务 | ~4 | 上下文压缩 |
| 其他服务 | ~15 | OAuth、插件、LSP 等 |

---

## 三、核心 Services 详解

### 3.1 API 客户端 (api/)

#### client.ts - Anthropic API 客户端

```typescript
export class AnthropicClient {
  private baseUrl: string
  private auth: AuthStrategy

  // 支持多种认证方式
  static create(config: ClientConfig): AnthropicClient {
    switch (config.auth.type) {
      case 'direct':
        return new DirectApiClient(config)
      case 'aws':
        return new AWSBedrockClient(config)
      case 'azure':
        return new AzureFoundryClient(config)
      case 'vertex':
        return new VertexAIClient(config)
      default:
        throw new Error(`Unknown auth type: ${config.auth.type}`)
    }
  }

  // 流式调用
  async *createMessage(
    params: CreateMessageParams
  ): AsyncGenerator<StreamEvent> {
    const response = await this.fetch('/v1/messages', {
      method: 'POST',
      body: JSON.stringify(params),
      headers: {
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json',
      }
    })

    // 处理流式响应
    for await (const line of response.body) {
      yield parseEvent(line)
    }
  }
}
```

#### withRetry.ts - 重试逻辑

```typescript
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    backoff = 'exponential',
    retryableErrors = DEFAULT_RETRYABLE_ERRORS
  } = options

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      if (!isRetryable(error, retryableErrors)) {
        throw error
      }

      if (attempt < maxRetries) {
        const delay = calculateDelay(attempt, baseDelay, maxDelay, backoff)
        await sleep(delay)
      }
    }
  }

  throw lastError
}

// 可重试的错误
const DEFAULT_RETRYABLE_ERRORS = [
  'rate_limit_error',
  'internal_error',
  'service_unavailable'
]
```

### 3.2 MCP 服务 (mcp/)

#### client.ts - MCP 客户端实现

```typescript
export class MCPClient {
  private transport: MCPTransport

  // 支持多种传输方式
  static async create(config: MCPConfig): Promise<MCPClient> {
    switch (config.transport.type) {
      case 'stdio':
        return new StdIOClient(config)
      case 'http':
        return new HTTPSSEClient(config)
      case 'websocket':
        return new WebSocketClient(config)
    }
  }

  // 工具调用
  async callTool(name: string, args: Record<string, unknown>): Promise<ToolResult> {
    await this.send({
      jsonrpc: '2.0',
      id: generateId(),
      method: 'tools/call',
      params: { name, arguments: args }
    })

    const response = await this.receive()
    return response.result
  }

  // 资源读取
  async readResource(uri: string): Promise<ResourceContent> {
    // ...
  }

  // 订阅通知
  async subscribeToNotification(callback: NotificationCallback): Promise<void> {
    // ...
  }
}
```

#### types.ts - MCP 类型定义

```typescript
// MCP 协议类型
interface MCPRequest {
  jsonrpc: '2.0'
  id: string | number
  method: string
  params?: Record<string, unknown>
}

interface MCPResponse {
  jsonrpc: '2.0'
  id: string | number
  result?: unknown
  error?: MCPError
}

interface MCPError {
  code: number
  message: string
  data?: unknown
}

// 工具相关类型
interface MCPTool {
  name: string
  description: string
  inputSchema: JSONSchema
}

// 资源相关类型
interface MCPResource {
  uri: string
  name: string
  description?: string
  mimeType?: string
}
```

### 3.3 分析服务 (analytics/)

#### index.ts - 分析主入口

```typescript
export class AnalyticsService {
  private sinks: AnalyticsSink[] = []

  constructor(config: AnalyticsConfig) {
    // 初始化多个接收器
    if (config.datadogEnabled) {
      this.sinks.push(new DatadogSink(config.datadog))
    }
    if (config.internalEnabled) {
      this.sinks.push(new InternalSink(config.internal))
    }
  }

  // 记录事件
  async track(event: AnalyticsEvent): Promise<void> {
    // 添加上下文
    const enrichedEvent = this.enrichEvent(event)

    // 发送到所有接收器
    await Promise.all(
      this.sinks.map(sink => sink.send(enrichedEvent))
    )
  }

  // 记录页面视图
  async trackPageView(page: string, properties?: Record<string, unknown>): Promise<void> {
    await this.track({
      type: 'page_view',
      name: page,
      properties,
      timestamp: Date.now()
    })
  }

  // 记录用户操作
  async trackAction(action: string, properties?: Record<string, unknown>): Promise<void> {
    await this.track({
      type: 'action',
      name: action,
      properties,
      timestamp: Date.now()
    })
  }
}
```

#### growthbook.ts - GrowthBook 特性开关

```typescript
export class GrowthBookService {
  private client: GrowthBookClient

  constructor(apiKey: string) {
    this.client = new GrowthBookClient(apiKey)
  }

  // 获取特性开关值
  getFeature<T>(featureKey: string, defaultValue: T): T {
    return this.client.getFeatureValue(featureKey, defaultValue)
  }

  // 判断特性是否启用
  isFeatureEnabled(featureKey: string): boolean {
    return this.client.isEnabled(featureKey)
  }

  // 获取特性变量
  getFeatureVariables<T>(featureKey: string): T | null {
    return this.client.getFeatureVariables(featureKey)
  }
}
```

### 3.4 压缩服务 (compact/)

#### compact.ts - 主压缩逻辑

```typescript
export class CompactService {
  // Snip 压缩 - 删除不重要的消息
  async snip(messages: Message[], options: SnipOptions): Promise<CompactionResult> {
    // 1. 分析消息重要性
    const importanceScores = messages.map(msg => calculateImportance(msg))

    // 2. 选择要删除的消息
    const toRemove = selectMessagesByImportance(importanceScores, options.targetTokens)

    // 3. 创建新的消息列表
    return {
      messages: messages.filter(msg => !toRemove.has(msg.id)),
      removedCount: toRemove.size,
      freedTokens: calculateFreedTokens(toRemove)
    }
  }

  // Context Collapse - 深度压缩
  async collapseContext(messages: Message[], options: CollapseOptions): Promise<CompactionResult> {
    // 1. 分组消息
    const groups = groupMessages(messages)

    // 2. 压缩每个组
    const compressed = await Promise.all(
      groups.map(group => compressGroup(group))
    )

    return { messages: compressed.flat(), removedCount: 0 }
  }

  // Auto Compact - 自动压缩
  async autoCompact(messages: Message[], context: ToolUseContext): Promise<AutoCompactResult> {
    const tokenCount = await countTokens(messages)
    const threshold = getTokenThreshold(context.getAppState())

    if (tokenCount > threshold) {
      // 执行压缩
      const result = await this.snip(messages, { targetTokens: threshold * 0.8 })
      return { executed: true, result }
    }

    return { executed: false }
  }
}
```

---

## 四、状态管理

### 4.1 Store 实现 (state/store.ts)

```typescript
// 简单观察者模式 Store
export type Store<T> = {
  getState: () => T
  setState: (updater: (prev: T) => T) => void
  subscribe: (listener: Listener) => () => void
}

export function createStore<T>(initialState: T): Store<T> {
  let state = initialState
  const listeners = new Set<Listener>()

  return {
    getState: () => state,

    setState: (updater) => {
      state = updater(state)
      listeners.forEach(listener => listener(state))
    },

    subscribe: (listener) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    }
  }
}
```

### 4.2 AppState 结构 (state/AppStateStore.ts)

```typescript
interface AppState {
  // 基础设置
  settings: Settings
  mainLoopModel: string
  verbose: boolean

  // 任务管理
  tasks: Record<string, TaskState>
  foregroundedTaskId: string

  // MCP 和插件
  mcp: {
    clients: MCPServerConnection[]
    tools: Tools
  }
  plugins: {
    enabled: string[]
    disabled: string[]
  }

  // 远程桥接
  replBridgeEnabled: boolean
  replBridgeConnected: boolean

  // 通知
  notifications: {
    current: Notification | null
    queue: Notification[]
  }

  // 推测状态
  speculation: SpeculationState | null

  // 团队上下文
  teamContext: TeamContext | null
  teammates: TeammateState[]
}
```

### 4.3 选择器 (state/selectors.ts)

```typescript
// 获取查看的队友任务
export function getViewedTeammateTask(appState: AppState): InProcessTeammateTaskState | undefined {
  const taskId = appState.viewingAgentTaskId
  return taskId ? appState.tasks[taskId] as InProcessTeammateTaskState : undefined
}

// 确定输入路由目标
export function getActiveAgentForInput(appState: AppState): ActiveAgentForInput {
  if (appState.viewingAgentTaskId) {
    return { type: 'viewed', taskId: appState.viewingAgentTaskId }
  }
  if (appState.foregroundedTaskId) {
    return { type: 'foreground', taskId: appState.foregroundedTaskId }
  }
  return { type: 'leader' }
}
```

---

## 五、组件间通信方式

### 5.1 状态驱动通信

```
AppState (单例 Store)
    │
    ├── useAppState(selector)  ──> 读取状态
    │
    └── useSetAppState()       ──> 更新状态
```

### 5.2 事件驱动通信

```typescript
// 消息队列
class MessageQueueManager {
  private queue: Command[] = []
  private listeners: Set<(cmd: Command) => void> = new Set()

  subscribe(listener: (cmd: Command) => void): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  enqueue(command: Command) {
    this.queue.push(command)
    this.listeners.forEach(l => l(command))
  }
}

// 使用 Hook
function useCommandQueue() {
  return useSyncExternalStore(
    messageQueue.subscribe,
    () => messageQueue.getLatest()
  )
}
```

### 5.3 组合 Hook 模式

```typescript
// 复杂功能通过组合多个 Hook 实现
function useMergedTools(initialTools: Tools, mcpTools: Tools, permissionContext?: Context): Tools {
  const assembledTools = useAssembleToolPool(initialTools, mcpTools)
  const filteredTools = useToolPermissions(assembledTools, permissionContext)
  return useMemo(() => deduplicate(filteredTools), [filteredTools])
}
```

---

## 六、Python 版本实现建议

### 6.1 Hooks 映射

| TypeScript | Python | 说明 |
|------------|--------|------|
| `useAppState` | `use_app_state()` | 读取状态（函数式） |
| `useSetAppState` | `set_app_state()` | 更新状态 |
| `useSettings` | `get_settings()` | 获取设置 |
| `useRemoteSession` | `RemoteSession` | 远程会话类 |
| `useMergedTools` | `merge_tools()` | 合并工具函数 |

### 6.2 Services 映射

| TypeScript | Python | 说明 |
|------------|--------|------|
| `AnthropicClient` | `AnthropicClient` | API 客户端 |
| `MCPClient` | `MCPClient` | MCP 客户端 |
| `AnalyticsService` | `AnalyticsService` | 分析服务 |
| `CompactService` | `CompactService` | 压缩服务 |
| `Store<T>` | `Store[T]` | 泛型 Store |

### 6.3 建议的包结构

```
claudex/
├── core/
│   ├── __init__.py
│   ├── state/
│   │   ├── __init__.py
│   │   ├── store.py       # Store 实现
│   │   ├── app_state.py   # AppState 定义
│   │   └── selectors.py   # 选择器函数
│   │
│   ├── hooks/
│   │   ├── __init__.py
│   │   ├── state.py       # 状态 hooks
│   │   ├── remote.py      # 远程连接
│   │   └── tools.py       # 工具管理
│   │
│   └── services/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── retry.py
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── types.py
│       ├── analytics/
│       │   └── __init__.py
│       └── compact/
│           └── __init__.py
```

### 6.4 关键实现要点

1. **状态管理**: 使用简单的观察者模式实现 Store
2. **Hook 模拟**: 使用 Python 函数模拟 Hook 行为
3. **服务层**: 使用类和异步函数
4. **类型安全**: 使用 dataclass 和 Protocol
5. **依赖注入**: 服务通过参数注入

---

*文档版本: 1.0*
*分析时间: 2026-04-08*