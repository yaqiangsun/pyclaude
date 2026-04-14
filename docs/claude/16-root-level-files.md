# 根目录文件分析

本文档分析 `src/` 目录下的根级别 TypeScript 文件（不在子目录中的文件）。

---

## 一、根目录文件列表

| 文件 | 大小 | 功能 |
|------|------|------|
| **QueryEngine.ts** | 46KB | 核心查询引擎 (已在02覆盖) |
| **Task.ts** | 3KB | 任务定义 (已在02覆盖) |
| **Tool.ts** | 29KB | 工具系统 (已在02覆盖) |
| **commands.ts** | 25KB | 命令系统 (已在02覆盖) |
| **history.ts** | 14KB | 历史记录 (已在02覆盖) |
| **query.ts** | 68KB | 核心查询循环 (已在02覆盖) |
| **tools.ts** | 17KB | 工具注册 (已在06覆盖) |
| **main.tsx** | 803KB | 主入口 (已在09覆盖) |
| **setup.ts** | 20KB | 初始化 (已在09覆盖) |
| **context.ts** | 6KB | Context 导出聚合 |
| **cost-tracker.ts** | 68KB | 成本追踪 |
| **costHook.ts** | 0.6KB | 成本 Hook |
| **dialogLaunchers.tsx** | 25KB | 对话框启动器 |
| **interactiveHelpers.tsx** | 57KB | 交互助手 |
| **projectOnboardingState.ts** | 6KB | 项目引导状态 |
| **replLauncher.tsx** | 3KB | REPL 启动器 |
| **ink.ts** | 3KB | Ink 导出 |
| **replLauncher.tsx** | 2KB | REPL 启动器 |

---

## 二、cost-tracker.ts - 成本追踪

### 2.1 功能概述

成本追踪模块用于追踪 API 使用成本、Token 消耗、代码变更行数等指标。

### 2.2 核心函数

```typescript
// 从 bootstrap/state 导入的函数
getTotalCostUSD, getTotalDuration, getTotalAPIDuration
getTotalLinesAdded, getTotalLinesRemoved
getTotalInputTokens, getTotalOutputTokens
getModelUsage, getUsageForModel

// 成本计算
addToTotalSessionCost(cost: number, usage: Usage, model: string): number

// 会话持久化
getStoredSessionCosts(sessionId: string): StoredCostState | undefined
restoreCostStateForSession(sessionId: string): boolean
saveCurrentSessionCosts(fpsMetrics?: FpsMetrics): void

// 格式化输出
formatTotalCost(): string
```

### 2.3 数据结构

```typescript
type StoredCostState = {
  totalCostUSD: number
  totalAPIDuration: number
  totalAPIDurationWithoutRetries: number
  totalToolDuration: number
  totalLinesAdded: number
  totalLinesRemoved: number
  lastDuration: number | undefined
  modelUsage: { [modelName: string]: ModelUsage } | undefined
}

type ModelUsage = {
  inputTokens: number
  outputTokens: number
  cacheReadInputTokens: number
  cacheCreationInputTokens: number
  webSearchRequests: number
  costUSD: number
  contextWindow: number
  maxOutputTokens: number
}
```

### 2.4 成本计算

```typescript
// 计算单个模型的使用成本
addToTotalSessionCost(cost, usage, model):
  - 累加输入/输出 Token
  - 累加缓存读写 Token
  - 累加 Web 搜索次数
  - 计算Advisor成本（递归）
  - 更新分析服务指标
```

---

## 三、costHook.ts - 成本摘要

### 3.1 功能

```typescript
export function useCostSummary(
  getFpsMetrics?: () => FpsMetrics | undefined,
): void {
  // 进程退出时输出成本摘要
  // 保存会话成本到项目配置
}
```

---

## 四、projectOnboardingState.ts - 项目引导状态

### 4.1 功能

管理新项目的引导流程，帮助用户完成初始设置。

### 4.2 引导步骤

```typescript
type Step = {
  key: string           // 步骤标识
  text: string          // 步骤描述
  isComplete: boolean   // 是否完成
  isCompletable: boolean // 是否可完成
  isEnabled: boolean    // 是否启用
}

// 步骤1: workspace - 创建新应用或克隆仓库
// 步骤2: claudemd - 创建 CLAUDE.md 文件
```

### 4.3 核心函数

```typescript
getSteps(): Step[]                    // 获取所有引导步骤
isProjectOnboardingComplete(): boolean // 检查是否完成
maybeMarkProjectOnboardingComplete(): void // 标记完成
shouldShowProjectOnboarding(): boolean    // 是否显示引导
incrementProjectOnboardingSeenCount(): void // 增加显示计数
```

---

## 五、dialogLaunchers.tsx - 对话框启动器

### 5.1 设计目的

将 `main.tsx` 中的对话框组件动态导入抽离，实现代码分割和性能优化。

### 5.2 启动器函数

```typescript
// 代理内存快照更新对话框
launchSnapshotUpdateDialog(root, props):
  -> SnapshotUpdateDialog

// 设置验证错误对话框
launchInvalidSettingsDialog(root, props):
  -> InvalidSettingsDialog

// Bridge 会话选择对话框
launchAssistantSessionChooser(root, props):
  -> AssistantSessionChooser

// Assistant 安装向导
launchAssistantInstallWizard(root):
  -> NewInstallWizard

// Teleport 恢复包装器
launchTeleportResumeWrapper(root):
  -> TeleportResumeWrapper

// 仓库不匹配对话框
launchTeleportRepoMismatchDialog(root, props):
  -> TeleportRepoMismatchDialog
```

### 5.3 实现模式

```typescript
export async function launchXxxDialog(root: Root, props: Props): Promise<Result> {
  const { XxxDialog } = await import('./components/XxxDialog.js');
  return showSetupDialog<Result>(root, done =>
    <XxxDialog {...props} onComplete={done} onCancel={() => done(null)} />
  );
}
```

---

## 六、replLauncher.tsx - REPL 启动器

### 6.1 功能

动态导入并启动主 REPL 界面。

### 6.2 实现

```typescript
export async function launchRepl(
  root: Root,
  appProps: AppWrapperProps,
  replProps: REPLProps,
  renderAndRun: (root: Root, element: React.ReactNode) => Promise<void>
): Promise<void> {
  const { App } = await import('./components/App.js')
  const { REPL } = await import('./screens/REPL.js')

  await renderAndRun(root, (
    <App {...appProps}>
      <REPL {...replProps} />
    </App>
  ))
}
```

### 6.3 Props 类型

```typescript
type AppWrapperProps = {
  getFpsMetrics: () => FpsMetrics | undefined
  stats?: StatsStore
  initialState: AppState
}
```

---

## 七、interactiveHelpers.tsx - 交互助手

### 7.1 功能概述

提供交互式界面的通用辅助函数，包括对话框、错误退出、引导流程等。

### 7.2 核心函数

```typescript
// 完成引导
completeOnboarding(): void

// 显示对话框
showDialog<T>(root, renderer): Promise<T>

// 显示设置对话框（带 AppStateProvider + KeybindingSetup）
showSetupDialog<T>(root, renderer, options?): Promise<T>

// 渲染并运行
renderAndRun(root, element): Promise<void>

// 错误退出
exitWithError(root, message, beforeExit?): Promise<never>
exitWithMessage(root, message, options?): Promise<never>

// 显示设置屏幕
showSetupScreens(
  root,
  permissionMode,
  allowDangerouslySkipPermissions,
  commands?,
  claudeInChrome?,
  devChannels?
): Promise<boolean>
```

### 7.3 showSetupScreens 流程

```typescript
async function showSetupScreens(root, ...):
  // 1. 检查是否跳过（测试模式/demo模式）
  // 2. 显示 Onboarding（首次运行时）
  // 3. 显示 TrustDialog（工作区信任）
  // 4. 初始化 GrowthBook
  // 5. 显示 MCP 服务器审批
  // 6. 处理 Claude.md 外部包含警告
  // 7. 显示主题选择
  // 8. 显示项目引导
  // 9. 处理 Chrome 扩展集成
  return true/false
```

---

## 八、context.ts - Context 导出

### 8.1 功能

聚合导出所有 Context Provider。

```typescript
// 重新导出 context/ 目录中的 Provider
export { StatsStoreProvider } from './context/stats.js'
export { FpsMetricsProvider } from './context/fpsMetrics.js'
export { NotificationsProvider } from './context/notifications.js'
// ...
```

---

## 九、ink.ts - Ink 导出

### 9.1 功能

聚合导出 Ink 框架的核心类型和组件。

```typescript
export type { Root, RenderOptions, TextProps } from './ink/ink.js'
export { render, Box, Text } from './ink/ink.js'
// ...
```

---

## 十、Python 版本实现建议

### 10.1 成本追踪

```python
# claudex/tracking/cost.py
from dataclasses import dataclass, field
from typing import Dict
import time

@dataclass
class ModelUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    web_search_requests: int = 0
    cost_usd: float = 0.0
    context_window: int = 0
    max_output_tokens: int = 0

class CostTracker:
    def __init__(self):
        self._total_cost_usd: float = 0.0
        self._total_duration: float = 0.0
        self._total_api_duration: float = 0.0
        self._total_lines_added: int = 0
        self._total_lines_removed: int = 0
        self._model_usage: Dict[str, ModelUsage] = {}

    def add_session_cost(self, cost: float, usage: dict, model: str):
        self._total_cost_usd += cost
        if model not in self._model_usage:
            self._model_usage[model] = ModelUsage()
        u = self._model_usage[model]
        u.input_tokens += usage.get('input_tokens', 0)
        u.output_tokens += usage.get('output_tokens', 0)
        # ...

    def get_total_cost(self) -> float:
        return self._total_cost_usd

    def format_total_cost(self) -> str:
        # 格式化成本输出
        pass

    def save_session_costs(self, session_id: str):
        # 保存到项目配置
        pass

    def restore_session_costs(self, session_id: str) -> bool:
        # 从项目配置恢复
        pass
```

### 10.2 项目引导

```python
# claudex/onboarding/project.py
from dataclasses import dataclass
from typing import List
import os

@dataclass
class OnboardingStep:
    key: str
    text: str
    is_complete: bool
    is_completable: bool
    is_enabled: bool

class ProjectOnboarding:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir

    def get_steps(self) -> List[OnboardingStep]:
        has_claude_md = os.path.exists(
            os.path.join(self.project_dir, 'CLAUDE.md')
        )
        is_empty = len(os.listdir(self.project_dir)) == 0
        return [
            OnboardingStep('workspace', '...', False, True, is_empty),
            OnboardingStep('claudemd', '...', has_claude_md, True, not is_empty),
        ]

    def is_complete(self) -> bool:
        return all(
            s.is_complete for s in self.get_steps()
            if s.is_completable and s.is_enabled
        )
```

### 10.3 目录结构

```
cludex/
├── tracking/
│   ├── __init__.py
│   ├── cost.py          # CostTracker
│   └── hooks.py         # Cost summary hook
├── onboarding/
│   ├── __init__.py
│   └── project.py       # ProjectOnboarding
├── ui/
│   ├── __init__.py
│   ├── dialogs.py       # Dialog launchers
│   ├── repl.py          # REPL launcher
│   └── helpers.py       # Interactive helpers
└── context/
    └── __init__.py      # Context exports
```

---

## 十一、模块汇总

| 文件 | 功能 | 复杂度 |
|------|------|--------|
| cost-tracker.ts | API成本/Token追踪 | 中 |
| costHook.ts | 成本摘要Hook | 低 |
| projectOnboardingState.ts | 项目引导 | 低 |
| dialogLaunchers.tsx | 对话框启动器 | 中 |
| replLauncher.tsx | REPL启动器 | 低 |
| interactiveHelpers.tsx | 交互助手 | 中 |
| context.ts | Context导出 | 低 |
| ink.ts | Ink导出 | 低 |

---

*文档版本: 1.0*
*分析时间: 2026-04-14*