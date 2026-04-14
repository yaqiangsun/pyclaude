# 输入系统分析

本文档分析 Claude Code 的输入系统：快捷键（Keybindings）、Vim 模式、服务器模块。

---

## 一、keybindings 目录 - 快捷键系统

### 1.1 目录结构

```
src/keybindings/
├── defaultBindings.ts      # 默认快捷键定义
├── loadUserBindings.ts     # 用户自定义快捷键加载
├── useKeybinding.ts        # 快捷键 Hook
├── useShortcutDisplay.ts   # 快捷键显示 Hook
├── KeybindingContext.tsx   # Context Provider
├── KeybindingProviderSetup.tsx  # Provider 初始化
├── resolver.ts             # 快捷键解析
├── parser.ts               # 快捷键解析器
├── match.ts                # 快捷键匹配
├── schema.ts               # JSON Schema
├── template.ts             # 模板
├── validate.ts             # 验证
├── types.ts                # 类型定义
└── shortcutFormat.ts       # 快捷键格式
```

### 1.2 默认快捷键

```typescript
// src/keybindings/defaultBindings.ts
export const DEFAULT_BINDINGS: KeybindingBlock[] = [
  {
    context: 'Global',
    bindings: {
      // 全局
      'ctrl+c': 'app:interrupt',      // 中断
      'ctrl+d': 'app:exit',           // 退出
      'ctrl+l': 'app:redraw',         // 重绘
      'ctrl+t': 'app:toggleTodos',    // 切换 TODO
      'ctrl+o': 'app:toggleTranscript',  // 切换 transcript

      // 历史
      'ctrl+r': 'history:search',     // 历史搜索

      // 文件导航
      'ctrl+p': 'file:quickOpen',
      'ctrl+g': 'file:gotoLine',

      // 编辑
      'ctrl+u': 'edit:undo',
      'ctrl+w': 'edit:deleteWord',

      // ...更多
    }
  },
  {
    context: 'Input',
    bindings: {
      'ctrl+a': 'input:beginningOfLine',
      'ctrl+e': 'input:endOfLine',
      'ctrl+k': 'input:killToEnd',
      // ...
    }
  }
]
```

### 1.3 快捷键解析

```typescript
// 快捷键格式示例
'ctrl+shift+c'    // 组合键
'ctrl+c, ctrl+d'  // 序列键
'cmd+option+f'    // macOS 特定

// 解析结果
interface ParsedKeybinding {
  modifiers: Set<'ctrl' | 'shift' | 'alt' | 'meta'>
  key: string
  sequence?: string[]
}
```

### 1.4 Context Provider

```typescript
// KeybindingContext.tsx
export const KeybindingContext = createContext<KeybindingContext>()

export function useKeybinding(action: string): Keybinding | undefined {
  const context = useContext(KeybindingContext)
  return context.getBinding(action)
}
```

---

## 二、vim 目录 - Vim 模式

### 2.1 目录结构

```
src/vim/
├── types.ts           # 类型定义 (状态机)
├── motions.ts         # 动作定义
├── operators.ts       # 操作符定义
├── textObjects.ts     # 文本对象
├── transitions.ts     # 状态转换
└── [其他文件]
```

### 2.2 Vim 状态机

```typescript
// src/vim/types.ts
export type VimState =
  | { mode: 'INSERT'; insertedText: string }
  | { mode: 'NORMAL'; command: CommandState }

// CommandState 状态图:
// idle ──┬─[d/c/y]──► operator
//        ├─[1-9]────► count
//        ├─[fFtT]───► find
//        ├─[g]──────► g
//        ├─[r]──────► replace
//        └─[><]─────► indent
```

### 2.3 操作符

```typescript
// operators.ts
export type Operator = 'delete' | 'change' | 'yank'

// 操作符组合:
// d + w = 删除单词
// c + i + " = 修改引号内
// y + y = 复制行
```

### 2.4 动作

```typescript
// motions.ts
export type Motion =
  | 'h' | 'j' | 'k' | 'l'     // 左下上右
  | 'w' | 'b' | 'e'           // 词移动
  | '0' | '$'                 // 行首/行尾
  | 'gg' | 'G'                // 文件头/尾
  | 'f' | 'F' | 't' | 'T'    // 查找
```

### 2.5 文本对象

```typescript
// textObjects.ts
export type TextObjScope = 'inner' | 'around'

// 文本对象:
// iw = inner word
// aw = around word
// i" = inner quotes
// a" = around quotes
// i( = inner parentheses
// ip = inner paragraph
```

---

## 三、server 目录 - 服务器模式

### 3.1 目录结构

```
src/server/
├── createDirectConnectSession.ts  # 创建直连会话
├── directConnectManager.ts        # 会话管理器
└── types.ts                       # 类型定义
```

### 3.2 服务器配置

```typescript
// types.ts
export type ServerConfig = {
  port: number
  host: string
  authToken: string
  unix?: string              // Unix socket
  idleTimeoutMs?: number     // 空闲超时
  maxSessions?: number       // 最大会话数
  workspace?: string         // 默认工作目录
}
```

### 3.3 会话状态

```typescript
export type SessionState =
  | 'starting'    // 启动中
  | 'running'     // 运行中
  | 'detached'    // 已分离
  | 'stopping'    // 停止中
  | 'stopped'     // 已停止

export type SessionInfo = {
  id: string
  status: SessionState
  createdAt: number
  workDir: string
  process: ChildProcess | null
  sessionKey?: string
}
```

### 3.4 直连模式

```typescript
// createDirectConnectSession.ts
// 创建与现有 Claude Code 进程的直连会话
// 用于 IDE 集成、远程控制等场景
```

---

## 四、moreright 目录 - 右键菜单

### 4.1 目录结构

```
src/moreright/
└── useMoreRight.tsx   # MoreRight 菜单 Hook
```

### 4.2 功能

```typescript
// 右键上下文菜单
// 在终端中显示更多操作选项
export function useMoreRight() {
  // 打开菜单
  // 获取菜单项
  // 处理选择
}
```

---

## 五、migrations 目录 - 数据迁移

### 5.1 目录结构

```
src/migrations/
├── migrateAutoUpdatesToSettings.ts
├── migrateBypassPermissionsAcceptedToSettings.ts
├── migrateFennecToOpus.ts
├── migrateLegacyOpusToCurrent.ts
├── migrateOpusToOpus1m.ts
├── migrateSonnet1mToSonnet45.ts
├── migrateSonnet45ToSonnet46.ts
├── resetAutoModeOptInForDefaultOffer.ts
└── resetProToOpusDefault.ts
```

### 5.2 迁移模式

```typescript
// 迁移接口
interface Migration {
  version: string
  description: string

  // 检查是否需要迁移
  shouldRun(): Promise<boolean>

  // 执行迁移
  run(): Promise<void>

  // 回滚 (可选)
  rollback?(): Promise<void>
}
```

---

## 六、Python 版本实现建议

### 6.1 快捷键系统

```python
# claudex/ui/keybindings/__init__.py
from dataclasses import dataclass
from typing import Callable
from enum import Enum

class Modifier(Enum):
    CTRL = "ctrl"
    SHIFT = "shift"
    ALT = "alt"
    META = "meta"

@dataclass
class Keybinding:
    key: str
    modifiers: set[Modifier]
    action: str
    description: str

class KeybindingManager:
    def __init__(self):
        self._bindings: dict[str, Keybinding] = {}
        self._load_defaults()

    def register(self, action: str, binding: Keybinding):
        self._bindings[action] = binding

    def resolve(self, key: str, modifiers: set[Modifier]) -> str | None:
        # 查找匹配的 action
        for action, binding in self._bindings.items():
            if binding.key == key and binding.modifiers == modifiers:
                return action
        return None

    def get_binding(self, action: str) -> Keybinding | None:
        return self._bindings.get(action)
```

### 6.2 Vim 模式

```python
# claudex/ui/vim/__init__.py
from dataclasses import dataclass
from enum import Enum
from typing import Literal

class VimMode(Enum):
    INSERT = "INSERT"
    NORMAL = "NORMAL"

@dataclass
class VimState:
    mode: VimMode
    # NORMAL 模式
    command_buffer: str = ""
    count: int = 0
    operator: str | None = None
    # INSERT 模式
    inserted_text: str = ""

class VimEngine:
    def __init__(self):
        self.state = VimState(mode=VimMode.NORMAL)

    def feed(self, key: str) -> str | None:
        """处理按键,返回要插入的文本或 None"""
        if self.state.mode == VimMode.INSERT:
            return self._handle_insert(key)
        return self._handle_normal(key)

    def _handle_normal(self, key: str) -> str | None:
        # 状态机处理
        # 返回动作结果
        pass

    def mode(self) -> VimMode:
        return self.state.mode
```

### 6.3 服务器模式

```python
# claudex/server/__init__.py
from dataclasses import dataclass
from enum import Enum
from typing import AsyncGenerator

class SessionState(Enum):
    STARTING = "starting"
    RUNNING = "running"
    DETACHED = "detached"
    STOPPING = "stopping"
    STOPPED = "stopped"

@dataclass
class SessionInfo:
    id: str
    status: SessionState
    created_at: float
    work_dir: str
    session_key: str | None = None

class DirectConnectServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.sessions: dict[str, SessionInfo] = {}

    async def create_session(self, work_dir: str) -> SessionInfo:
        # 创建新会话
        pass

    async def attach_session(self, session_id: str) -> AsyncGenerator:
        # 附加到现有会话
        pass

    async def detach_session(self, session_id: str):
        # 分离会话
        pass
```

### 6.4 目录结构

```
claudex/ui/keybindings/
├── __init__.py
├── manager.py        # KeybindingManager
├── defaults.py       # 默认快捷键
└── parser.py         # 解析器

claudex/ui/vim/
├── __init__.py
├── state.py          # VimState
├── engine.py         # VimEngine
├── motions.py        # 动作
├── operators.py      # 操作符
└── textobjects.py    # 文本对象

claudex/server/
├── __init__.py
├── config.py         # ServerConfig
├── session.py        # SessionInfo
└── manager.py        # DirectConnectServer

claudex/migrations/
├── __init__.py
└── runner.py         # MigrationRunner
```

---

## 七、模块总结

| 目录 | 功能 | 复杂度 |
|------|------|--------|
| **keybindings/** | 快捷键系统 | 中 |
| **vim/** | Vim 模式状态机 | 中 |
| **server/** | 直连服务器 | 低 |
| **moreright/** | 右键菜单 | 低 |
| **migrations/** | 数据迁移 | 低 |

---

*文档版本: 1.0*
*分析时间: 2026-04-14*