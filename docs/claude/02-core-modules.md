# 核心模块详细分析

本文档详细分析 Claude Code 的六个核心模块：QueryEngine、Task、Tool、commands、query 和 history。

---

## 一、QueryEngine.ts - 核心查询引擎

### 1.1 文件概述

- **位置**: `src/QueryEngine.ts`
- **职责**: 管理对话生命周期和会话状态，是 Claude Code 的核心引擎
- **特点**: 从 `ask()` 函数提取的独立类，可同时用于 headless/SDK 和 REPL

### 1.2 核心类定义

```typescript
export class QueryEngine {
  // 配置
  private config: QueryEngineConfig

  // 状态
  private mutableMessages: Message[]           // 可变消息列表
  private abortController: AbortController     // 中止控制器
  private permissionDenials: SDKPermissionDenial[]  // 权限拒绝记录
  private totalUsage: NonNullableUsage         // 总使用量
  private hasHandledOrphanedPermission = false // 是否处理过孤立权限
  private readFileState: FileStateCache        // 文件状态缓存
  private discoveredSkillNames = new Set<string>()  // 发现的技能名称
  private loadedNestedMemoryPaths = new Set<string>()  // 已加载的嵌套内存路径

  // 构造函数
  constructor(config: QueryEngineConfig) {
    this.config = config
    this.abortController = config.abortController ?? new AbortController()
    this.readFileState = config.readFileCache ?? new FileStateCache()
    // 初始化消息
    this.mutableMessages = [...(config.initialMessages ?? [])]
  }
}
```

### 1.3 QueryEngineConfig 配置结构

```typescript
export type QueryEngineConfig = {
  // 基础配置
  cwd: string                    // 工作目录
  tools: Tools                   // 可用工具列表
  commands: Command[]            // 可用命令
  mcpClients: MCPServerConnection[]  // MCP 客户端
  agents: AgentDefinition[]      // Agent 定义

  // 权限和状态回调
  canUseTool: CanUseToolFn       // 权限检查函数
  getAppState: () => AppState    // 获取应用状态
  setAppState: (f: (prev: AppState) => AppState) => void  // 更新应用状态

  // 初始化数据
  initialMessages?: Message[]    // 初始消息
  readFileCache: FileStateCache  // 文件缓存

  // Prompt 配置
  customSystemPrompt?: string    // 自定义系统提示
  appendSystemPrompt?: string    // 追加系统提示

  // 模型配置
  userSpecifiedModel?: string    // 用户指定的模型
  fallbackModel?: string         // 回退模型
  thinkingConfig?: ThinkingConfig  // 思考配置

  // 预算限制
  maxTurns?: number              // 最大轮次
  maxBudgetUsd?: number          // 最大预算（美元）
  taskBudget?: { total: number } // 任务预算

  // 其他选项
  jsonSchema?: Record<string, unknown>  // JSON Schema
  verbose?: boolean               // 详细模式
  replayUserMessages?: boolean    // 重放用户消息
  handleElicitation?: ToolUseContext['handleElicitation']
  includePartialMessages?: boolean  // 包含部分消息
  setSDKStatus?: (status: SDKStatus) => void  // 设置 SDK 状态
  abortController?: AbortController  // 中止控制器
  orphanedPermission?: OrphanedPermission  // 孤立权限
  snipReplay?: (...) -> { messages: Message[]; executed: boolean } | undefined
}
```

### 1.4 核心方法

#### submitMessage - 提交消息（异步生成器）

```typescript
async function* submitMessage(
  this: QueryEngine,
  prompt: string | MessageLike,
  options?: {
    appendToHistory?: boolean
    isRestart?: boolean
    skipInitialResponse?: boolean
  }
): AsyncGenerator<SDKMessage, void, unknown>
```

**功能流程**:
1. 准备消息（用户输入转为 Message 对象）
2. 追加到消息历史
3. 调用 `query()` 函数生成响应
4. 逐个 yield SDK 消息
5. 更新状态（usage、权限拒绝等）

#### interrupt - 中断查询

```typescript
interrupt(): void {
  this.abortController.abort()
}
```

#### getMessages - 获取消息历史

```typescript
getMessages(): Message[] {
  return [...this.mutableMessages]
}
```

#### getReadFileState - 获取文件状态

```typescript
getReadFileState(): FileStateCache {
  return this.readFileState
}
```

#### setModel - 设置模型

```typescript
setModel(model: string): void {
  this.config.userSpecifiedModel = model
}
```

### 1.5 ask() 便捷函数

```typescript
export async function* ask({
  // 与 QueryEngineConfig 相同的参数
  cwd,
  tools,
  commands,
  // ...
}): AsyncGenerator<SDKMessage, void, unknown> {
  const engine = new QueryEngine(config)
  yield* engine.submitMessage(prompt, options)
}
```

---

## 二、Task.ts - 任务定义

### 2.1 文件概述

- **位置**: `src/Task.ts`
- **职责**: 定义任务系统的基础类型和工具函数
- **关键导出**: 任务类型、状态、生成器函数

### 2.2 任务类型定义

```typescript
export type TaskType =
  | 'local_bash'           // 本地 Bash 命令执行
  | 'local_agent'          // 本地 Agent
  | 'remote_agent'         // 远程 Agent
  | 'in_process_teammate'  // 进程内队友（Swarm 功能）
  | 'local_workflow'       // 本地工作流
  | 'monitor_mcp'          // MCP 监控任务
  | 'dream'                // 梦境模式（后台思考）
```

### 2.3 任务状态定义

```typescript
export type TaskStatus =
  | 'pending'     // 待处理
  | 'running'     // 运行中
  | 'completed'   // 已完成
  | 'failed'      // 失败
  | 'killed'      // 已终止
```

### 2.4 任务状态基础

```typescript
export type TaskStateBase = {
  id: string                    // 任务唯一 ID
  type: TaskType                // 任务类型
  status: TaskStatus            // 任务状态
  description: string           // 描述
  toolUseId?: string            // 对应的工具使用 ID
  startTime: number             // 开始时间戳
  endTime?: number              // 结束时间戳
  totalPausedMs?: number        // 总暂停时间
  outputFile: string            // 输出文件路径
  outputOffset: number          // 输出偏移量
  notified: boolean             // 是否已通知用户
}
```

### 2.5 任务 ID 生成算法

```typescript
const TASK_ID_PREFIXES: Record<TaskType, string> = {
  local_bash: 'b',
  local_agent: 'a',
  remote_agent: 'r',
  in_process_teammate: 't',
  local_workflow: 'w',
  monitor_mcp: 'm',
  dream: 'd',
}

const TASK_ID_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'

export function generateTaskId(type: TaskType): string {
  const prefix = getTaskIdPrefix(type)
  const bytes = randomBytes(8)  // 8 字节加密随机
  let id = prefix
  for (let i = 0; i < 8; i++) {
    id += TASK_ID_ALPHABET[bytes[i]! % 36]
  }
  return id
}
```

**ID 格式示例**: `b8f3a2c1d` (前缀 + 8位随机字符)
**组合空间**: 36^8 ≈ 2.8 万亿

### 2.6 任务上下文

```typescript
export type TaskContext = {
  abortController: AbortController
  getAppState: () => AppState
  setAppState: SetAppState
}
```

---

## 三、Tool.ts - 工具系统

### 3.1 文件概述

- **位置**: `src/Tool.ts`
- **职责**: 定义工具接口、构建工具、工具查找
- **特点**: 完整的工具生命周期管理，包括权限检查、渲染、执行

### 3.2 工具接口定义

```typescript
export type Tool<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // ======== 名称和元数据 ========
  readonly name: string
  aliases?: string[]
  searchHint?: string
  isMcp?: boolean
  isLsp?: boolean
  readonly shouldDefer?: boolean
  readonly alwaysLoad?: boolean
  mcpInfo?: { serverName: string; toolName: string }
  maxResultSizeChars: number
  readonly strict?: boolean

  // ======== 核心执行 ========
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>

  description(
    input: z.infer<Input>,
    options: {...}
  ): Promise<string>

  readonly inputSchema: Input
  readonly inputJSONSchema?: ToolInputJSONSchema
  outputSchema?: z.ZodType<unknown>

  // ======== 能力定义 ========
  inputsEquivalent?(a: z.infer<Input>, b: z.infer<Input>): boolean
  isConcurrencySafe(input: z.infer<Input>): boolean
  isEnabled(): boolean
  isReadOnly(input: z.infer<Input>): boolean
  isDestructive?(input: z.infer<Input>): boolean
  interruptBehavior?(): 'cancel' | 'block'
  isSearchOrReadCommand?(input: z.infer<Input>): {...}
  isOpenWorld?(input: z.infer<Input>): boolean
  requiresUserInteraction?(): boolean

  // ======== 权限和验证 ========
  validateInput?(input: z.infer<Input>, context: ToolUseContext): Promise<ValidationResult>
  checkPermissions(input: z.infer<Input>, context: ToolUseContext): Promise<PermissionResult>
  getPath?(input: z.infer<Input>): string
  preparePermissionMatcher?(input: z.infer<Input>): Promise<(pattern: string) => boolean>
  backfillObservableInput?(input: Record<string, unknown>): void

  // ======== 渲染和 UI ========
  prompt(options: {...}): Promise<string>
  userFacingName(input: Partial<z.infer<Input>> | undefined): string
  userFacingNameBackgroundColor?(input: ...): keyof Theme | undefined
  isTransparentWrapper?(): boolean
  getToolUseSummary?(input: ...): string | null
  getActivityDescription?(input: ...): string | null
  toAutoClassifierInput(input: z.infer<Input>): unknown
  mapToolResultToToolResultBlockParam(content: Output, toolUseID: string): ToolResultBlockParam
  renderToolResultMessage?(content: Output, progressMessagesForMessage: ProgressMessage<P>[], options: {...}): React.ReactNode
  extractSearchText?(out: Output): string
  renderToolUseMessage(input: Partial<z.infer<Input>>, options: {...}): React.ReactNode
  isResultTruncated?(output: Output): boolean
  renderToolUseTag?(input: Partial<z.infer<Input>>): React.ReactNode
  renderToolUseProgressMessage?(progressMessagesForMessage: ProgressMessage<P>[], options: {...}): React.ReactNode
  renderToolUseQueuedMessage?(): React.ReactNode
  renderToolUseRejectedMessage?(input: z.infer<Input>, options: {...}): React.ReactNode
  renderToolUseErrorMessage?(result: ..., options: {...}): React.ReactNode
  renderGroupedToolUse?(toolUses: Array<{...}>, options: {...}): React.ReactNode | null
}
```

### 3.3 工具构建器

```typescript
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (...): Promise<PermissionResult> =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?: unknown) => '',
  userFacingName: (_input?: unknown) => '',
}

export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
  return { ...TOOL_DEFAULTS, userFacingName: () => def.name, ...def } as BuiltTool<D>
}
```

### 3.4 工具函数

```typescript
// 工具名称匹配
export function toolMatchesName(
  tool: { name: string; aliases?: string[] },
  name: string,
): boolean {
  return tool.name === name || (tool.aliases?.includes(name) ?? false)
}

// 工具查找
export function findToolByName(tools: Tools, name: string): Tool | undefined {
  return tools.find(t => toolMatchesName(t, name))
}
```

### 3.5 ToolUseContext - 工具执行上下文

```typescript
export type ToolUseContext = {
  options: {
    commands: Command[]
    debug: boolean
    mainLoopModel: string
    tools: Tools
    verbose: boolean
    thinkingConfig: ThinkingConfig
    mcpClients: MCPServerConnection[]
    mcpResources: Record<string, ServerResource[]>
    isNonInteractiveSession: boolean
    agentDefinitions: AgentDefinitionsResult
    maxBudgetUsd?: number
    customSystemPrompt?: string
    appendSystemPrompt?: string
    querySource?: QuerySource
    refreshTools?: () => Tools
  }
  abortController: AbortController
  readFileState: FileStateCache
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  setAppStateForTasks?: (...)
  handleElicitation?: (...)
  setToolJSX?: SetToolJSXFn
  addNotification?: (notif: Notification) => void
  appendSystemMessage?: (...)
  // ... 更多字段
}
```

---

## 四、commands.ts - 命令系统

### 4.1 文件概述

- **位置**: `src/commands.ts`
- **职责**: 命令注册、加载、过滤、查找
- **规模**: 100+ 命令实现

### 4.2 命令类型定义

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
  getPromptForCommand(args: string, context: GetPromptForCommandContext): Promise<PromptContent[]>
  whenToUse?: string
  hasUserSpecifiedDescription?: boolean
  disableModelInvocation?: boolean
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

### 4.3 命令注册机制

```typescript
const COMMANDS = memoize((): Command[] => [
  addDir,
  advisor,
  autofixPr,
  backfillSessions,
  // ... 100+ commands
])

export async function getCommands(cwd: string): Promise<Command[]> {
  const allCommands = await loadAllCommands(cwd)
  const dynamicSkills = getDynamicSkills()
  const baseCommands = allCommands.filter(
    _ => meetsAvailabilityRequirement(_) && isCommandEnabled(_),
  )
  // 过滤重复的动态技能
  // ...
  return baseCommands
}
```

### 4.4 技能工具命令

```typescript
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
```

### 4.5 常用命令示例

| 命令 | 类型 | 功能 |
|------|------|------|
| `/commit` | prompt | 创建 git 提交 |
| `/config` | local-jsx | 打开配置面板 |
| `/help` | local-jsx | 显示帮助 |
| `/mcp` | local-jsx | MCP 服务器管理 |
| `/clear` | local | 清除对话 |
| `/resume` | local-jsx | 恢复会话 |

---

## 五、query.ts - 核心查询循环

### 5.1 文件概述

- **位置**: `src/query.ts`
- **职责**: 核心查询循环，与 API 交互，执行工具，处理上下文压缩
- **特点**: 约 1800 行代码，最复杂的模块之一

### 5.2 查询参数

```typescript
export type QueryParams = {
  messages: Message[]
  systemPrompt: SystemPrompt
  userContext: { [k: string]: string }
  systemContext: { [k: string]: string }
  canUseTool: CanUseToolFn
  toolUseContext: ToolUseContext
  fallbackModel?: string
  querySource: QuerySource
  maxOutputTokensOverride?: number
  maxTurns?: number
  skipCacheWrite?: boolean
  taskBudget?: { total: number }
  deps?: QueryDeps
}
```

### 5.3 主查询函数

```typescript
export async function* query(
  params: QueryParams,
): AsyncGenerator<
  | StreamEvent           // API 流式事件
  | RequestStartEvent     // 请求开始事件
  | Message               // 完整消息
  | TombstoneMessage      // 墓碑消息（删除标记）
  | ToolUseSummaryMessage // 工具使用摘要
  ,
  Terminal
>
```

### 5.4 核心循环逻辑 (queryLoop)

```typescript
async function* queryLoop(params: QueryParams): AsyncGenerator<...> {
  // 1. 预处理阶段
  await preQueryPreprocessing()

  // 2. API 调用阶段
  const stream = callClaudeAPI(params)
  for await (const event of stream) {
    if (event.type === 'content_block_start') {
      // 处理内容块开始
    }
    if (event.type === 'content_block_delta') {
      // 处理增量内容
    }
    if (event.type === 'tool_use') {
      // 处理工具调用
    }
  }

  // 3. 工具执行阶段
  for (const toolUse of toolUseBlocks) {
    const result = await executeTool(toolUse, context)
    yield { type: 'tool_result', toolUseId: toolUse.id, result }
  }

  // 4. 递归继续
  yield* queryLoop(updatedParams)
}
```

### 5.5 上下文压缩流程

```typescript
async function handleCompression(params) {
  // 1. Snip 压缩 - 删除不重要的消息
  const { compactionResult, snipTokensFreed } = await snip(messages, context)

  // 2. Micro Compact - 快速压缩
  const microCompactResult = await microCompact(messages, context)

  // 3. Context Collapse - 深度压缩
  const collapseResult = await collapseContext(messages, options)

  // 4. Auto Compact - 自动压缩
  const { compactionResult, consecutiveFailures } = await autocompact(...)
}
```

### 5.6 错误恢复机制

| 错误类型 | 恢复策略 |
|----------|----------|
| `max_output_tokens` | 逐步增加输出令牌限制 |
| `prompt_too_long` | 先尝试 context collapse，再尝试 reactive compact |
| 模型回退错误 | 触发 fallbackModel 重试 |

### 5.7 性能优化

- **流式工具执行**: `StreamingToolExecutor` 边流式传输边执行
- **技能预取**: 文件操作时发现技能
- **内存预取**: 加载相关内存附件
- **内存保留**: dumpPromptsFetch 只保留最新请求体

---

## 六、history.ts - 历史记录

### 6.1 文件概述

- **位置**: `src/history.ts`
- **职责**: 管理用户提示历史记录，包括历史读取、写入、粘贴内容处理

### 6.2 核心数据类型

```typescript
type StoredPastedContent = {
  id: number
  type: 'text' | 'image'
  content?: string           // 小型粘贴的内联内容
  contentHash?: string       // 大型粘贴的哈希引用
  mediaType?: string
  filename?: string
}

type LogEntry = {
  display: string
  pastedContents: Record<number, StoredPastedContent>
  timestamp: number
  project: string
  sessionId?: string
}

export type TimestampedHistoryEntry = {
  display: string
  timestamp: number
  resolve: () => Promise<HistoryEntry>
}
```

### 6.3 核心函数

#### addToHistory - 添加历史记录

```typescript
export function addToHistory(command: HistoryEntry | string): void {
  if (isEnvTruthy(process.env.CLAUDE_CODE_SKIP_PROMPT_HISTORY)) {
    return  // tmux 环境中跳过历史
  }
  // 添加到待写入队列
  // 注册清理函数，等待 flush 完成
}
```

#### getHistory - 获取历史记录

```typescript
export async function* getHistory(): AsyncGenerator<HistoryEntry> {
  // 当前会话条目先返回
  // 其他会话条目后返回
  // 最多 MAX_HISTORY_ITEMS = 100 条
}
```

#### getTimestampedHistory - 获取带时间戳的历史

```typescript
export async function* getTimestampedHistory(): AsyncGenerator<TimestampedHistoryEntry> {
  // ctrl+r 搜索使用，去重显示文本
}
```

### 6.4 粘贴内容处理

```typescript
// 获取粘贴内容的行数
export function getPastedTextRefNumLines(text: string): number

// 格式化文本引用
export function formatPastedTextRef(id: number, numLines: number): string
export function formatImageRef(id: number): string

// 解析引用
export function parseReferences(input: string): Array<{ id: number; match: string; index: number }>

// 展开引用
export function expandPastedTextRefs(input: string, pastedContents: Record<number, PastedContent>): string
```

### 6.5 撤销功能

```typescript
export function removeLastFromHistory(): void {
  // 用于 Esc 中断时撤销历史记录
  // 快速路径：从待处理缓冲区弹出
  // 慢速路径：添加到跳过集合
}
```

### 6.6 存储机制

- **存储格式**: `history.jsonl` (JSON Lines)
- **按项目区分**: 每个项目独立的历史文件
- **写入策略**: 批量刷新，待写入缓冲区
- **大小限制**:
  - 小型粘贴（<=1024 字符）直接内联
  - 大型粘贴计算哈希存到 paste store

---

## 七、模块间依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        commands.ts                               │
│   (命令注册、加载、过滤)                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    skills/            commands/          plugins/
    (技能)             (命令实现)          (插件)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        history.ts                                │
│              (历史记录管理)                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QueryEngine.ts                              │
│                   (查询引擎)                                      │
│         - 使用 Tool.ts 类型                                       │
│         - 调用 query.ts                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        query.ts                                  │
│                   (核心查询循环)                                  │
│  - 与 API 交互                                                   │
│  - 工具执行 (Tool.ts)                                            │
│  - 上下文压缩                                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    Task.ts            Tool.ts           history.ts
    (任务类型)         (工具定义)         (历史)
```

---

## 八、Python 版本实现建议

### 8.1 核心类型映射

| TypeScript | Python | 说明 |
|------------|--------|------|
| `QueryEngine` | `class QueryEngine` | 查询引擎类 |
| `QueryEngineConfig` | `@dataclass QueryEngineConfig` | 配置数据类 |
| `Tool` | `Protocol Tool` | 工具抽象基类 |
| `TaskType` | `TaskType(Enum)` | 任务类型枚举 |
| `Message` | `dataclass Message` | 消息数据类 |

### 8.2 关键实现要点

1. **QueryEngine**: 保持异步生成器模式，实现消息流式处理
2. **Tool**: 使用 ABC 或 Protocol 定义接口，支持泛型
3. **Task**: 使用 Enum 定义任务类型，使用 dataclass
4. **query**: 核心循环需要支持流式处理和工具执行
5. **history**: 使用 JSONL 文件存储，考虑线程安全

### 8.3 建议的文件结构

```
claudex/
├── core/
│   ├── __init__.py
│   ├── query_engine.py    # QueryEngine
│   ├── query.py           # query 函数
│   ├── tool.py            # Tool 接口和构建器
│   ├── task.py            # 任务类型
│   └── history.py         # 历史记录
├── commands/
│   ├── __init__.py
│   ├── registry.py        # 命令注册
│   └── builtins/          # 内置命令
└── cli/
    ├── __init__.py
    └── transports/        # 传输层
```

---

*文档版本: 1.0*
*分析时间: 2026-04-08*