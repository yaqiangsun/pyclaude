# Bridge 桥接模块详细分析

本文档详细分析 Claude Code 的远程控制（Remote Control）功能的桥接/通信核心模块。

---

## 一、模块概述

### 1.1 功能定位

Bridge 模块负责 Claude Code CLI 与 claude.ai 云端服务之间的双向通信，实现远程控制功能。

### 1.2 目录结构

```
src/bridge/
├── bridgeMain.ts              # 独立桥接主循环
├── bridgeApi.ts               # Environments API 客户端
├── bridgeConfig.ts            # OAuth/URL 配置
├── bridgeEnabled.ts           # 特性开关
├── replBridge.ts              # REPL 桥接核心
├── remoteBridgeCore.ts        # 无环境（v2）桥接实现
├── initReplBridge.ts          # REPL 桥接初始化包装器
├── createSession.ts           # 会话 CRUD 操作
├── sessionRunner.ts           # 子进程会话管理
├── bridgeMessaging.ts         # 消息解析/路由/去重
├── replBridgeTransport.ts     # v1/v2 传输抽象
├── workSecret.ts              # Work Secret 编解码
├── jwtUtils.ts                # Token 刷新调度
├── pollConfig.ts              # 轮询参数配置
├── envLessBridgeConfig.ts     # v2 专用配置
├── types.ts                   # 类型定义
├── bridgeUI.ts                # UI 相关
├── bridgeDebug.ts             # 调试工具
├── codeSessionApi.ts          # Code Session API
└── ...                        # 其他辅助文件
```

### 1.3 两种桥接模式

| 模式 | 说明 | 主要文件 |
|------|------|----------|
| **Env-based (v1)** | 基于 Environments API | `bridgeMain.ts` |
| **Env-less (v2)** | 直接连接 Session Ingress | `remoteBridgeCore.ts` |

---

## 二、桥接模式详解

### 2.1 Env-based 模式 (v1)

工作流程：
```
1. 注册环境 (registerEnvironment)
2. 轮询工作 (pollForWork)
3. 确认工作 (acknowledgeWork)
4. 创建会话 (createSession)
5. 心跳保活 (heartbeatWork)
6. 处理完成
```

### 2.2 Env-less 模式 (v2 / CCR)

工作流程：
```
1. 直接连接 Session Ingress (/v1/code/sessions/*)
2. 跳过环境注册/轮询层
3. 更轻量，更简洁
```

---

## 三、核心 API 接口

### 3.1 BridgeApiClient 接口 (bridgeApi.ts)

```typescript
type BridgeApiClient = {
  // 环境管理
  registerBridgeEnvironment(config: BridgeConfig): Promise<Environment>
  deregisterEnvironment(environmentId: string): Promise<void>

  // 工作轮询
  pollForWork(
    environmentId: string,
    environmentSecret: string,
    signal?: AbortSignal,
    reclaimOlderThanMs?: number
  ): Promise<PollWorkResponse>

  acknowledgeWork(
    environmentId: string,
    workId: string,
    sessionToken: string
  ): Promise<void>

  stopWork(
    environmentId: string,
    workId: string,
    force?: boolean
  ): Promise<void>

  heartbeatWork(
    environmentId: string,
    workId: string,
    sessionToken: string
  ): Promise<void>

  // 会话管理
  sendPermissionResponseEvent(
    sessionId: string,
    event: SDKMessage,
    sessionToken: string
  ): Promise<void>

  archiveSession(sessionId: string): Promise<void>

  reconnectSession(
    environmentId: string,
    sessionId: string
  ): Promise<ReconnectResponse>
}
```

### 3.2 请求头配置

```typescript
// 标准请求头
const DEFAULT_HEADERS = {
  'anthropic-version': '2023-06-01',
  'anthropic-beta': 'environments-2025-11-01',
  'Content-Type': 'application/json',
}

// 认证
Authorization: Bearer ${accessToken}
X-Trusted-Device-Token: ${trustedDeviceToken}  // 可选
```

---

## 四、会话管理

### 4.1 会话创建 (createSession.ts)

```typescript
async function createBridgeSession({
  environmentId,
  title,
  events,
  gitRepoUrl,
  branch,
  signal,
  baseUrl?,
  getAccessToken?,
  permissionMode?
}): Promise<string | null>
```

**会话创建流程**:
1. POST `/v1/sessions` 创建会话
2. 返回 `session_id` (格式: `session_*` 或 `cse_*`)
3. 可选: PATCH 更新标题
4. 结束时: POST archive

### 4.2 会话运行器 (sessionRunner.ts)

```typescript
type SessionHandle = {
  // 会话 ID
  sessionId: string

  // 完成状态
  done: Promise<SessionDoneStatus>  // 'completed' | 'failed' | 'interrupted'

  // 控制方法
  kill(): void
  forceKill(): void

  // 活动状态
  activities: SessionActivity[]      // 最近10个活动
  currentActivity: SessionActivity | null

  // 认证
  accessToken: string               // session_ingress_token

  // stderr 缓冲
  lastStderr: string[]              // 最近10行

  // 输入输出
  writeStdin(data: string): void
  updateAccessToken(token: string): void
}
```

**超时配置**:
- 默认: 24 小时 (`DEFAULT_SESSION_TIMEOUT_MS`)
- 可配置: `sessionTimeoutMs`

---

## 五、消息格式和传递

### 5.1 REPL 传输层 (replBridgeTransport.ts)

支持两种传输协议：

#### v1 传输: HybridTransport
- WebSocket 读取 (Session-Ingress)
- POST 写入

#### v2 传输: SSETransport + CCRClient
- SSE 流式读取
- CCRClient 批量写入 + 心跳 + 状态报告

### 5.2 消息类型 (bridgeMessaging.ts)

```typescript
// SDK 消息类型
type SDKMessage =
  | UserMessage
  | AssistantMessage
  | SystemMessage
  | ToolUseMessage
  | ToolResultMessage
  | ContentBlock
  | SDKControlRequest
  | SDKControlResponse

// 消息类型判断
isSDKMessage(value)           // SDKMessage 类型守卫
isSDKControlResponse(value)   // 控制响应
isSDKControlRequest(value)    // 控制请求
```

### 5.3 控制请求类型

```typescript
type SDKControlRequest = {
  request_id: string
  request: {
    subtype: 'initialize'
           | 'set_model'
           | 'set_max_thinking_tokens'
           | 'set_permission_mode'
           | 'interrupt'
           | 'can_use_tool'
  }
}
```

### 5.4 消息去重 (BoundedUUIDSet)

```typescript
class BoundedUUIDSet {
  // FIFO 环形缓冲区，O(1) 添加/查询
  // 防止重复消息
}
```

---

## 六、配置和初始化

### 6.1 配置管理 (bridgeConfig.ts)

```typescript
// OAuth/URL 配置
getBridgeAccessToken()  // 支持开发覆盖 (CLAUDE_BRIDGE_OAUTH_TOKEN)
getBridgeBaseUrl()      // 支持开发覆盖 (CLAUDE_BRIDGE_BASE_URL)
```

### 6.2 轮询配置 (pollConfig.ts)

```typescript
type PollIntervalConfig = {
  pollIntervalMs: number      // 默认 3000ms
  heartbeatIntervalMs: number // 默认 30000ms
  reclaimOlderThanMs: number  // 默认 120000ms
}
```

### 6.3 特性开关 (bridgeEnabled.ts)

```typescript
// 主开关
tengu_ccr_bridge

// v2 模式
tengu_bridge_repl_v2

// 多会话支持
tengu_ccr_bridge_multi_session

// ID 兼容层
tengu_bridge_repl_v2_cse_shim_enabled
```

### 6.4 初始化流程

**initReplBridge.ts**:
```
1. 检查运行时启用状态 (isBridgeEnabledBlocking)
2. 验证 OAuth 认证
3. 检查组织策略 (allow_remote_control)
4. 检查版本兼容性
5. 根据 v2/v1 分支选择实现
6. 调用核心初始化
```

**replBridge.ts**:
```
1. 创建或恢复会话
2. 获取 worker JWT
3. 建立传输连接
4. 设置心跳/刷新调度
5. 注册回调处理
```

---

## 七、JWT 和令牌管理

### 7.1 Token 刷新调度器 (jwtUtils.ts)

```typescript
// Token 刷新调度器
createTokenRefreshScheduler({
  getAccessToken,
  onRefresh,
  label,
  refreshBufferMs = 5min  // 过期前5分钟刷新
})
```

**刷新策略**:
- 主动刷新: 过期前 5 分钟触发
- 后续刷新: 每 30 分钟一次
- 失败重试: 最多 3 次，间隔 60s

### 7.2 JWT 解析

```typescript
decodeJwtExpiry(token)    // 解码 exp 声明
decodeJwtPayload(token)   // 解码 payload
```

---

## 八、错误处理

### 8.1 错误类型

```typescript
class BridgeFatalError extends Error {
  status: number
  errorType?: string  // e.g. "environment_expired"
}
```

### 8.2 常见错误码

| 状态码 | 说明 | 处理策略 |
|--------|------|----------|
| 401 | 未认证 | 刷新 OAuth Token 重试 |
| 403 | 禁止 | 检查过期或权限 |
| 404 | 未找到 | 环境或会话不存在 |
| 410 | 已过期 | 环境已过期 |
| 429 | 限流 | 退避重试 |

### 8.3 错误判断函数

```typescript
isExpiredErrorType(errorType)  // 过期相关
isSuppressible403(err)         // 可忽略的权限错误
```

---

## 九、Work Secret 协议

### 9.1 Work Secret 结构 (workSecret.ts)

```typescript
type WorkSecret = {
  version: number
  session_ingress_token: string  // JWT
  api_base_url: string
  sources: Array<{
    type: string
    git_info?: {...}
  }>
  auth: Array<{
    type: string
    token: string
  }>
  claude_code_args?: Record<string, string>
  mcp_config?: unknown
  environment_variables?: Record<string, string>
  use_code_sessions?: boolean
}
```

### 9.2 编解码

```typescript
encodeWorkSecret(secret: WorkSecret): string  // Base64 编码
decodeWorkSecret(encoded: string): WorkSecret // Base64 解码
```

---

## 十、安全性考虑

### 10.1 安全措施

| 措施 | 说明 |
|------|------|
| ID 验证 | `validateBridgeId()` 防止路径遍历 |
| Token 刷新 | 自动处理 JWT 过期 |
| 可信设备 | 支持 `X-Trusted-Device-Token` |
| 消息去重 | BoundedUUIDSet 防止回音 |
| 错误脱敏 | 不向用户暴露敏感服务端错误 |

### 10.2 输入验证

```typescript
validateBridgeId(id: string): boolean  // 防止路径遍历攻击
```

---

## 十一、关键文件总结

| 文件 | 作用 | 关键导出 |
|------|------|----------|
| `bridgeMain.ts` | 独立桥接主循环 | `runBridgeMainLoop()` |
| `replBridge.ts` | REPL 桥接核心 | `initReplBridge()`, `ReplBridge` |
| `remoteBridgeCore.ts` | 无环境桥接 | `initRemoteBridgeCore()` |
| `initReplBridge.ts` | 初始化包装 | `initReplBridge()` |
| `bridgeApi.ts` | API 客户端 | `BridgeApiClient` |
| `bridgeConfig.ts` | OAuth/URL配置 | `getBridgeAccessToken()` |
| `createSession.ts` | 会话CRUD | `createBridgeSession()` |
| `sessionRunner.ts` | 子进程管理 | `SessionHandle` |
| `bridgeMessaging.ts` | 消息处理 | `handleIngressMessage()` |
| `replBridgeTransport.ts` | 传输抽象 | `Transport`, `getTransportForUrl()` |
| `workSecret.ts` | Work Secret | `encodeWorkSecret()`, `decodeWorkSecret()` |
| `jwtUtils.ts` | Token刷新 | `createTokenRefreshScheduler()` |
| `bridgeEnabled.ts` | 特性开关 | `isBridgeEnabledBlocking()` |
| `pollConfig.ts` | 轮询参数 | `PollIntervalConfig` |

---

## 十二、Python 版本实现建议

### 12.1 模块映射

| TypeScript | Python | 说明 |
|------------|--------|------|
| `BridgeApiClient` | `class BridgeAPIClient` | API 客户端 |
| `SessionHandle` | `class SessionHandle` | 会话句柄 |
| `Transport` | `Protocol Transport` | 传输层抽象 |
| `replBridge.ts` | `repl_bridge.py` | REPL 桥接核心 |
| `bridgeApi.ts` | `api.py` | API 封装 |
| `sessionRunner.py` | `session_runner.py` | 会话运行器 |

### 12.2 建议的包结构

```
claudex/bridge/
├── __init__.py
├── api.py                 # Bridge API 客户端
├── repl_bridge.py         # REPL 桥接核心
├── session_runner.py      # 会话运行器
├── transport/
│   ├── __init__.py
│   ├── base.py           # Transport 抽象基类
│   ├── websocket.py      # WebSocket 传输
│   ├── sse.py           # SSE 传输
│   └── hybrid.py        # Hybrid 传输
├── config.py             # 配置管理
├── jwt_utils.py         # JWT 工具
├── messaging.py         # 消息处理
└── types.py             # 类型定义
```

### 12.3 关键实现要点

1. **异步生成器**: 保持 `async for` 流式处理模式
2. **传输抽象**: 使用 Protocol 或 ABC 定义 Transport 接口
3. **状态机**: 会话状态使用 Enum 或状态机管理
4. **错误重试**: 实现指数退避重试机制
5. **JWT 处理**: 使用 PyJWT 库处理 Token

---

*文档版本: 1.0*
*分析时间: 2026-04-08*