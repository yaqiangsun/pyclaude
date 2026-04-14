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
├── 05-hooks-services.md # Hooks 和 Services
├── 06-tools-implementation.md   # 内置工具实现
├── 07-utils-library.md  # 工具函数库
├── 08-constants.md      # 常量定义
├── 09-startup-flow.md   # 启动流程分析
├── 10-skills-system.md  # 技能系统
├── 11-components.md     # React 组件系统
├── 12-context-state.md  # Context 和 State
├── 13-additional-modules.md  # 其他模块 (Ink/Buddy/Coordinator)
├── 14-input-system.md   # 输入系统 (Keybindings/Vim/Server)
├── 15-remaining-modules.md  # 剩余模块 (Bootstrap/Memdir/Remote/Types)
└── 16-root-level-files.md   # 根目录文件 (cost-tracker/onboarding/dialogs)
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

### 第六层：内置工具实现

📄 **[06-tools-implementation.md](06-tools-implementation.md)**

#### 工具分类（45 个工具目录）
- 文件操作: FileRead, FileWrite, FileEdit, Glob, Grep
- 命令执行: Bash, PowerShell
- Agent 管理: AgentTool
- 任务管理: TaskCreate, TaskGet, TaskList, TaskOutput, TaskStop, TaskUpdate
- Web 功能: WebFetch, WebSearch
- 其他: Config, TodoWrite, Skill, LSP, MCP 等

#### 工具构建模式
- 使用 `buildTool()` 函数构建
- 工具目录标准结构 (ToolName.tsx, prompt.ts, constants.ts, utils.ts, UI.tsx)

#### 核心工具详解
- **BashTool**: Shell 命令执行，包含完整的权限和安全机制
- **FileReadTool**: 文件读取，支持图像、PDF、Jupyter Notebook
- **FileEditTool**: 文件编辑，支持原地编辑和正则替换
- **AgentTool**: 子 Agent 创建和管理

#### 工具能力系统
- 并发安全 (isConcurrencySafe)
- 只读检测 (isReadOnly)
- 破坏性操作 (isDestructive)
- 权限检查 (checkPermissions)

#### 工具渲染系统
- 工具使用消息渲染
- 工具结果消息渲染
- 进度消息渲染

---

### 第七层：工具函数库

📄 **[07-utils-library.md](07-utils-library.md)**

#### 统计信息
- 文件数量: 329 个 TypeScript 文件
- 子目录: 31 个

#### 核心子模块
- **bash/**: Bash 命令解析 (parser, ast, commands)
- **permissions/**: 权限系统 (PermissionResult, filesystem, shellRuleMatching)
- **git/**: Git 操作 (commit, push, diff, reset)
- **messages/**: 消息处理
- **model/**: 模型相关
- **task/**: 任务管理

#### 重要工具函数
- 文件操作: readFile, writeTextContent, expandPath
- 错误处理: ClaudeError, ShellError, isENOENT
- 环境检测: isEnvTruthy, isBareMode, getCwd
- 认证: auth, authPortable
- 设置: settingsSchema, getGlobalConfig

---

### 第八层：常量定义

📄 **[08-constants.md](08-constants.md)**

#### 常量文件 (22 个)
- **apiLimits.ts**: Anthropic API 限制（图像、PDF、媒体）
- **toolLimits.ts**: 工具结果大小限制
- **tools.ts**: 允许/禁止工具列表
- **betas.ts**: Beta 功能开关
- **system.ts**: 应用信息、超时
- **oauth.ts**: OAuth 配置
- **outputStyles.ts**: 输出样式
- **keys.ts**: 键盘快捷键
- **prompts.ts**: 系统提示词 (54KB)

#### 关键常量
- API 限制: IMAGE_MAX_WIDTH, PDF_MAX_PAGES, API_MAX_MEDIA_PER_REQUEST
- 工具限制: DEFAULT_MAX_RESULT_SIZE_CHARS, MAX_TOOL_RESULT_TOKENS
- 系统: APP_NAME, DEFAULT_TIMEOUT_MS

---

### 第九层：启动流程

📄 **[09-startup-flow.md](09-startup-flow.md)**

#### main.tsx (入口)
- 顶层副作用（性能分析、MDM 读取、Keychain 预取）
- CLI 参数解析（Commander.js）
- 主要命令结构

#### setup.ts (初始化)
- 版本检查（Node.js >= 18）
- UDS 消息服务器启动
- 队友模式快照
- 终端备份恢复
- Hooks 配置快照
- Worktree 创建（可选）
- 预加载命令和插件
- 分析服务初始化

#### launchRepl 流程
- 创建 Ink 应用
- 渲染应用
- 处理退出

---

### 第十层：技能系统

📄 **[10-skills-system.md](10-skills-system.md)**

#### 技能类型
- **bundled**: CLI 内置技能 (15+ 个)
- **skills/**: 用户/项目技能目录
- **commands/**: 传统命令目录 (兼容)
- **mcp**: MCP 服务器技能
- **plugin**: 插件技能

#### 核心内置技能
- **debug**: 调试当前会话
- **simplify**: 代码审查和清理（启动3个并行Agent）
- **verify**: 验证代码
- **loremIpsum**: 生成占位符
- **skillify**: 将命令转为技能
- **remember**: 记住信息
- 条件加载技能 (dream, hunter, loop 等)

#### 技能注册机制
- `registerBundledSkill()` 程序化注册
- Frontmatter 解析 (SKILL.md)
- 动态技能发现 (条件触发)
- 变量替换 (\${1}, \${CLAUDE_SKILL_DIR})

#### main.tsx (入口)
- 顶层副作用（性能分析、MDM 读取、Keychain 预取）
- CLI 参数解析（Commander.js）
- 主要命令结构

#### setup.ts (初始化)
- 版本检查（Node.js >= 18）
- UDS 消息服务器启动
- 队友模式快照
- 终端备份恢复
- Hooks 配置快照
- Worktree 创建（可选）
- 预加载命令和插件
- 分析服务初始化

#### launchRepl 流程
- 创建 Ink 应用
- 渲染应用
- 处理退出

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
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      10-skills-system.md                         │
│       内置技能 (15+)  │  磁盘技能加载  │  动态发现                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 核心类型映射（供 Python 实现参考）

| TypeScript | 位置 | Python 建议实现 |
|------------|------|-----------------|
| `QueryEngine` | 02-core-modules.md | `class QueryEngine` |
| `QueryEngineConfig` | 02-core-modules.md | `@dataclass` |
| `Tool` | 02-core-modules.md | `Protocol` / `ABC` |
| `TaskType` | 02-core-modules.md | `Enum` |
| `Message` | 02-core-modules.md | `dataclass` |
| `BridgeApiClient` | 03-bridge-module.md | `class` |
| `SessionHandle` | 03-bridge-module.md | `class` |
| `Transport` | 04-cli-commands.md | `Protocol` / `ABC` |
| `Command` | 04-cli-commands.md | `Protocol` / `ABC` |
| `Store<T>` | 05-hooks-services.md | `Generic[T]` |
| `AppState` | 05-hooks-services.md | `@dataclass` |
| `BashTool` | 06-tools-implementation.md | `class Tool` |
| `ToolRegistry` | 06-tools-implementation.md | `class ToolRegistry` |
| `PermissionResult` | 07-utils-library.md | `dataclass` |
| API 限制常量 | 08-constants.md | `const` 变量 |
| `setup()` | 09-startup-flow.md | `async def setup()` |
| `BundledSkillDefinition` | 10-skills-system.md | `dataclass` |
| `Skill` | 10-skills-system.md | `ABC` |
| `registerBundledSkill` | 10-skills-system.md | `def register_bundled_skill()` |
| `InkComponent` | 11-components.md | `ABC` |
| `MessageRenderer` | 11-components.md | `class` |
| `StatsStore` | 12-context-state.md | `class` |
| `NotificationManager` | 12-context-state.md | `class` |
| `ClaudePlugin` | 12-context-state.md | `Protocol` |
| `Screen` | 13-additional-modules.md | `class` |
| `KeybindingManager` | 14-input-system.md | `class` |
| `VimState` | 14-input-system.md | `dataclass` |
| `VimEngine` | 14-input-system.md | `class` |
| `ServerConfig` | 14-input-system.md | `dataclass` |
| `SessionInfo` | 14-input-system.md | `dataclass` |
| `Memory` | 15-remaining-modules.md | `dataclass` |
| `MemoryManager` | 15-remaining-modules.md | `class` |
| `RemoteSession` | 15-remaining-modules.md | `dataclass` |
| `PromptCommand` | 15-remaining-modules.md | `dataclass` |
| `LocalCommand` | 15-remaining-modules.md | `dataclass` |
| `ChannelEntry` | 15-remaining-modules.md | `dataclass` |
| `CostTracker` | 16-root-level-files.md | `class` |
| `ModelUsage` | 16-root-level-files.md | `dataclass` |
| `ProjectOnboarding` | 16-root-level-files.md | `class` |
| `OnboardingStep` | 16-root-level-files.md | `dataclass` |

---

## 建议阅读顺序

1. **初学者**: 01 → 02 → 06 → 10 → 11 → 14 → 15 → 16 → 03 → 04 → 05 → 07 → 08 → 09 → 12 → 13
2. **有经验者**: 直接查看感兴趣的部分
3. **Python 实现**: 重点参考 02-core-modules.md、06-tools-implementation.md、10-skills-system.md、11-components.md、14-input-system.md、15-remaining-modules.md、16-root-level-files.md 和模块依赖关系

> **新增文档说明**:
> - 06: 工具实现（45 个内置工具）
> - 07: 工具函数库（329 个工具函数）
> - 08: 常量定义（22 个常量文件）
> - 09: 启动流程（main.tsx + setup.ts）
> - 10: 技能系统（15+ 内置技能、磁盘加载、动态发现）
> - 11: React 组件系统（144 个组件）
> - 12: Context 和 State（Provider 模式、统计、通知）
> - 13: 其他模块（Ink 框架、Buddy 队友、Coordinator 协调者）
> - 14: 输入系统（Keybindings 快捷键、Vim 模式、Server 直连）
> - 15: 剩余模块（Bootstrap、Memdir 记忆、Remote 远程、Types 类型定义）
> - 16: 根目录文件（cost-tracker 成本追踪、projectOnboarding 项目引导、dialogLaunchers 对话框启动器）

---

## 相关资源

- 源代码: `/src/`
- 桥接模块: `/src/bridge/`
- CLI 模块: `/src/cli/`
- Hooks: `/src/hooks/`
- Services: `/src/services/`

---

*文档版本: 1.4*
*最后更新: 2026-04-14*