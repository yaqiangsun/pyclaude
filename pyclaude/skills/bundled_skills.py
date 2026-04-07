"""Bundled Skills."""
from __future__ import annotations
import os
import re
import random
from typing import Any, Callable, Optional

# One-token words for lorem ipsum (verified via API token counting)
ONE_TOKEN_WORDS = [
    # Articles & pronouns
    'the', 'a', 'an', 'I', 'you', 'he', 'she', 'it', 'we', 'they',
    'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our',
    'this', 'that', 'what', 'who',
    # Common verbs
    'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'can', 'could', 'may', 'might',
    'must', 'shall', 'should', 'make', 'made', 'get', 'got', 'go', 'went',
    'come', 'came', 'see', 'saw', 'know', 'take', 'think', 'look', 'want',
    'use', 'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need',
    'feel', 'seem', 'leave', 'put',
    # Common nouns & adjectives
    'time', 'year', 'day', 'way', 'man', 'thing', 'life', 'hand', 'part',
    'place', 'case', 'point', 'fact', 'good', 'new', 'first', 'last',
    'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big',
    'high', 'small', 'large', 'next', 'early', 'young', 'few', 'public',
    'bad', 'same', 'able',
    # Prepositions & conjunctions
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from', 'by', 'about',
    'like', 'through', 'over', 'before', 'between', 'under', 'since',
    'without', 'and', 'or', 'but', 'if', 'than', 'because', 'as', 'until',
    'while', 'so', 'though', 'both', 'each', 'when', 'where', 'why', 'how',
    # Common adverbs
    'not', 'now', 'just', 'more', 'also', 'here', 'there', 'then', 'only',
    'very', 'well', 'back', 'still', 'even', 'much', 'too', 'such',
    'never', 'again', 'most', 'once', 'off', 'away', 'down', 'out', 'up',
    # Tech/common words
    'test', 'code', 'data', 'file', 'line', 'text', 'word', 'number',
    'system', 'program', 'set', 'run', 'value', 'name', 'type', 'state',
    'end', 'start',
]

# Bundled skill definition
class BundledSkillDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        allowed_tools: Optional[list[str]] = None,
        argument_hint: Optional[str] = None,
        when_to_use: Optional[str] = None,
        model: Optional[str] = None,
        disable_model_invocation: bool = False,
        user_invocable: bool = True,
        hooks: Optional[list] = None,
        context: Optional[dict] = None,
        agent: Optional[dict] = None,
        is_enabled: Optional[Callable[[], bool]] = None,
        get_prompt_for_command: Optional[Callable] = None,
    ):
        self.name = name
        self.description = description
        self.allowed_tools = allowed_tools or []
        self.argument_hint = argument_hint
        self.when_to_use = when_to_use
        self.model = model
        self.disable_model_invocation = disable_model_invocation
        self.user_invocable = user_invocable
        self.hooks = hooks or []
        self.context = context or {}
        self.agent = agent
        self.is_enabled = is_enabled or (lambda: True)
        self.get_prompt_for_command = get_prompt_for_command


# Registry of bundled skills
BUNDLED_SKILLS: dict[str, BundledSkillDefinition] = {}


def register_bundled_skill(skill: BundledSkillDefinition) -> None:
    """Register a bundled skill."""
    BUNDLED_SKILLS[skill.name] = skill


def get_bundled_skill(name: str) -> Optional[BundledSkillDefinition]:
    """Get a bundled skill by name."""
    return BUNDLED_SKILLS.get(name)


def get_all_bundled_skills() -> list[BundledSkillDefinition]:
    """Get all bundled skills."""
    return list(BUNDLED_SKILLS.values())


def is_ant_user() -> bool:
    """Check if the current user is an ant (internal user)."""
    return os.environ.get('USER_TYPE') == 'ant'


def is_auto_memory_enabled() -> bool:
    """Check if auto-memory is enabled."""
    # Try to import from memdir.paths if available
    try:
        from pyclaude.memdir.paths import isAutoMemoryEnabled
        return isAutoMemoryEnabled()
    except ImportError:
        return False


# ============================================================
# Individual Skill Registration Functions
# ============================================================

def register_update_config_skill() -> None:
    """Register the update-config skill."""
    SETTINGS_EXAMPLES_DOCS = """## Settings File Locations

Choose the appropriate file based on scope:

| File | Scope | Git | Use For |
|------|-------|-----|---------|
| `~/.claude/settings.json` | Global | N/A | Personal preferences for all projects |
| `.claude/settings.json` | Project | Commit | Team-wide hooks, permissions, plugins |
| `.claude/settings.local.json` | Project | Gitignore | Personal overrides for this project |

Settings load in order: user → project → local (later overrides earlier).

## Settings Schema Reference

### Permissions
```json
{
  "permissions": {
    "allow": ["Bash(npm:*)", "Edit(.claude)", "Read"],
    "deny": ["Bash(rm -rf:*)"],
    "ask": ["Write(/etc/*)"],
    "defaultMode": "default" | "plan" | "acceptEdits" | "dontAsk",
    "additionalDirectories": ["/extra/dir"]
  }
}
```

### Environment Variables
```json
{
  "env": {
    "DEBUG": "true",
    "MY_API_KEY": "value"
  }
}
```

### Model & Agent
```json
{
  "model": "sonnet",
  "agent": "agent-name",
  "alwaysThinkingEnabled": true
}
```

### Attribution (Commits & PRs)
```json
{
  "attribution": {
    "commit": "Custom commit trailer text",
    "pr": "Custom PR description text"
  }
}
```

### MCP Server Management
```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["server1", "server2"],
  "disabledMcpjsonServers": ["blocked-server"]
}
```

### Plugins
```json
{
  "enabledPlugins": {
    "formatter@anthropic-tools": true
  }
}
```

### Other Settings
- `language`: Preferred response language
- `cleanupPeriodDays`: Days to keep transcripts (default: 30)
- `respectGitignore`: Whether to respect .gitignore (default: true)
"""

    HOOKS_DOCS = """## Hooks Configuration

Hooks run commands at specific points in Claude Code's lifecycle.

### Hook Structure
```json
{
  "hooks": {
    "EVENT_NAME": [
      {
        "matcher": "ToolName|OtherTool",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here",
            "timeout": 60,
            "statusMessage": "Running..."
          }
        ]
      }
    ]
  }
}
```

### Hook Events
- PermissionRequest - Run before permission prompt
- PreToolUse - Run before tool, can block
- PostToolUse - Run after successful tool
- PostToolUseFailure - Run after tool fails
- Notification - Run on notifications
- Stop - Run when Claude stops
- PreCompact/PostCompact - Before/after compaction
- UserPromptSubmit - When user submits
- SessionStart - When session starts

### Hook Types
1. **Command Hook** - Runs a shell command
2. **Prompt Hook** - Evaluates a condition with LLM
3. **Agent Hook** - Runs an agent with tools
"""

    UPDATE_CONFIG_PROMPT = f"""# Update Config Skill

Modify Claude Code configuration by updating settings.json files.

## When Hooks Are Required (Not Memory)

If the user wants something to happen automatically in response to an EVENT, they need a **hook** configured in settings.json.

**These require hooks:**
- "Before compacting, ask me what to preserve" → PreCompact hook
- "After writing files, run prettier" → PostToolUse hook
- "When I run bash commands, log them" → PreToolUse hook

## CRITICAL: Read Before Write

**Always read the existing settings file before making changes.** Merge new settings with existing ones.

## CRITICAL: Use AskUserQuestion for Ambiguity

When the user's request is ambiguous, use AskUserQuestion.

## Decision: Config Tool vs Direct Edit

**Use the Config tool** for: theme, editorMode, verbose, model, language, alwaysThinkingEnabled, permissions.defaultMode

**Edit settings.json directly** for: hooks, permissions rules, env vars, MCP config, plugins

## Workflow
1. Clarify intent
2. Read existing file
3. Merge carefully
4. Edit file
5. Confirm

{SETTINGS_EXAMPLES_DOCS}

{HOOKS_DOCS}

## Example Workflows

### Adding a Hook
User: "Format my code after Claude writes it"
1. Clarify: Which formatter? (prettier, gofmt, etc.)
2. Read: .claude/settings.json (or create if missing)
3. Merge: Add to existing hooks

### Adding Permissions
User: "Allow npm commands without prompting"
1. Read: Existing permissions
2. Merge: Add Bash(npm:*) to allow array
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        if args.startswith('[hooks-only]'):
            req = args[len('[hooks-only]'):].strip()
            prompt = HOOKS_DOCS
            if req:
                prompt += f'\n\n## Task\n\n{req}'
            return [{'type': 'text', 'text': prompt}]

        prompt = UPDATE_CONFIG_PROMPT
        if args:
            prompt += f'\n\n## User Request\n\n{args}'

        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='update-config',
        description='Use this skill to configure Claude Code via settings.json. For permissions, env vars, hooks, or any settings.json changes.',
        allowed_tools=['Read'],
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_debug_skill() -> None:
    """Register the debug skill."""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        # Debug skill returns basic prompt for diagnosing issues
        prompt = f"""# Debug Skill

Help the user debug an issue they're encountering in this Claude Code session.

## Session Debug Log
Debug logs are at: ~/.claude/debug/

## Issue Description
{args or 'The user did not describe a specific issue.'}

## Instructions
1. Review the user's issue description
2. Look for error patterns
3. Explain what you found in plain language
4. Suggest concrete fixes or next steps
"""
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='debug',
        description='Enable debug logging and help diagnose issues with Claude Code.',
        allowed_tools=['Read', 'Grep', 'Glob'],
        argument_hint='[issue description]',
        disable_model_invocation=True,
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_keybindings_skill() -> None:
    """Register the keybindings-help skill."""
    try:
        from pyclaude.keybindings.load_user_bindings import is_keybinding_customization_enabled
    except ImportError:
        is_keybinding_customization_enabled = lambda: False

    SECTION_INTRO = """# Keybindings Skill

Create or modify `~/.claude/keybindings.json` to customize keyboard shortcuts.

## CRITICAL: Read Before Write

**Always read `~/.claude/keybindings.json` first** (it may not exist yet). Merge changes with existing bindings.
"""

    SECTION_FILE_FORMAT = """## File Format
```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    {
      "context": "Chat",
      "bindings": {
        "ctrl+e": "chat:externalEditor"
      }
    }
  ]
}
```
"""

    SECTION_KEYSTROKE_SYNTAX = """## Keystroke Syntax

**Modifiers** (combine with `+`):
- `ctrl` (alias: `control`)
- `alt` (aliases: `opt`, `option`)
- `shift`
- `meta` (aliases: `cmd`, `command`)

**Special keys**: `escape`, `enter`, `return`, `tab`, `space`, `backspace`, `delete`, `up`, `down`, `left`, `right`

**Chords**: Space-separated keystrokes, e.g. `ctrl+k ctrl+s`
"""

    SECTION_UNBINDING = """## Unbinding Default Shortcuts
Set a key to `null` to remove its default binding:
```json
{
  "context": "Chat",
  "bindings": {
    "ctrl+s": null
  }
}
```
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        sections = [
            SECTION_INTRO,
            SECTION_FILE_FORMAT,
            SECTION_KEYSTROKE_SYNTAX,
            SECTION_UNBINDING,
            """## Behavioral Rules
1. Only include contexts the user wants to change
2. Validate that actions and contexts are known
3. Warn about reserved shortcuts
4. New bindings are additive
""",
        ]

        if args:
            sections.append(f'## User Request\n\n{args}')

        return [{'type': 'text', 'text': '\n\n'.join(sections)}]

    register_bundled_skill(BundledSkillDefinition(
        name='keybindings-help',
        description='Use when the user wants to customize keyboard shortcuts, rebind keys, or modify keybindings.json.',
        allowed_tools=['Read'],
        user_invocable=False,
        is_enabled=is_keybinding_customization_enabled,
        get_prompt_for_command=get_prompt,
    ))


def register_verify_skill() -> None:
    """Register the verify skill (ANT-only)."""
    if not is_ant_user():
        return

    VERIFY_PROMPT = """# Verify Skill

Verify a code change does what it should by running the app.

## Steps
1. Run `git diff` to see what changed
2. Review the changes for correctness
3. Run tests or verify the functionality works as expected
4. Report findings
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        parts = [VERIFY_PROMPT.strip()]
        if args:
            parts.append(f'## User Request\n\n{args}')
        return [{'type': 'text', 'text': '\n\n'.join(parts)}]

    register_bundled_skill(BundledSkillDefinition(
        name='verify',
        description='Verify a code change does what it should by running the app.',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_lorem_ipsum_skill() -> None:
    """Register the lorem-ipsum skill (ANT-only)."""
    if not is_ant_user():
        return

    def generate_lorem_ipsum(target_tokens: int) -> str:
        tokens = 0
        result = ''

        while tokens < target_tokens:
            sentence_length = 10 + int(random.random() * 11)
            words_in_sentence = 0

            for i in range(sentence_length):
                if tokens >= target_tokens:
                    break

                word = ONE_TOKEN_WORDS[int(random.random() * len(ONE_TOKEN_WORDS))]
                result += word
                tokens += 1
                words_in_sentence += 1

                if i == sentence_length - 1 or tokens >= target_tokens:
                    result += '. '
                else:
                    result += ' '

            if words_in_sentence > 0 and random.random() < 0.2 and tokens < target_tokens:
                result += '\n\n'

        return result.strip()

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        parsed = 0
        if args.strip():
            try:
                parsed = int(args)
            except ValueError:
                pass

        if args and (parsed <= 0):
            return [{'type': 'text', 'text': 'Invalid token count. Please provide a positive number (e.g., /lorem-ipsum 10000).'}]

        target_tokens = parsed if parsed > 0 else 10000
        capped_tokens = min(target_tokens, 500_000)

        if capped_tokens < target_tokens:
            text = f'Requested {target_tokens} tokens, but capped at 500,000 for safety.\n\n{generate_lorem_ipsum(capped_tokens)}'
        else:
            text = generate_lorem_ipsum(capped_tokens)

        return [{'type': 'text', 'text': text}]

    register_bundled_skill(BundledSkillDefinition(
        name='lorem-ipsum',
        description='Generate filler text for long context testing.',
        argument_hint='[token_count]',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_skillify_skill() -> None:
    """Register the skillify skill (ANT-only)."""
    if not is_ant_user():
        return

    SKILLIFY_PROMPT = """# Skillify

Capture this session's repeatable process into a reusable skill.

## Your Task

### Step 1: Analyze the Session
- What repeatable process was performed
- What the inputs/parameters were
- The distinct steps (in order)
- What tools and permissions were needed

### Step 2: Interview the User
Use AskUserQuestion to understand:
- Name and description for the skill
- High-level goals and success criteria
- Steps involved
- Where to save (repo vs user)
- Arguments if needed
- Trigger phrases

### Step 3: Write the SKILL.md
Create at the location chosen in Step 2.

Format:
```markdown
---
name: {{skill-name}}
description: {{one-line description}}
allowed-tools: {{list of tool permissions}}
when_to_use: {{when to auto-invoke}}
argument-hint: "{{hint}}"
arguments: {{arg names}}
---

# Skill Title
Description

## Inputs
- `$arg_name`: Description

## Goal
Goal statement

## Steps

### 1. Step Name
What to do
**Success criteria**: What proves this step is done
```
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = SKILLIFY_PROMPT
        if args:
            prompt += f'\n\nThe user described this process as: "{args}"'
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='skillify',
        description="Capture this session's repeatable process into a skill.",
        allowed_tools=['Read', 'Write', 'Edit', 'Glob', 'Grep', 'AskUserQuestion'],
        user_invocable=True,
        disable_model_invocation=True,
        argument_hint='[description of the process]',
        get_prompt_for_command=get_prompt,
    ))


def register_remember_skill() -> None:
    """Register the remember skill."""

    SKILL_PROMPT = """# Memory Review

## Goal
Review the user's memory landscape and produce a clear report of proposed changes. Do NOT apply changes.

## Steps

### 1. Gather all memory layers
Read CLAUDE.md and CLAUDE.local.md from the project root (if they exist).

### 2. Classify each auto-memory entry
| Destination | What belongs there |
|-------------|-------------------|
| CLAUDE.md | Project conventions for all contributors |
| CLAUDE.local.md | Personal instructions, not for others |
| Stay in auto-memory | Working notes, temporary context |

### 3. Identify cleanup opportunities
- Duplicates: entries already in CLAUDE.md → propose removing
- Outdated: entries contradicted by newer ones → propose update
- Conflicts: contradictions between layers → propose resolution

### 4. Present the report
Output grouped by action type:
1. Promotions - entries to move
2. Cleanup - duplicates, outdated, conflicts
3. Ambiguous - need user input
4. No action needed

## Rules
- Present ALL proposals before making changes
- Do NOT modify files without explicit user approval
- Ask about ambiguous entries
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = SKILL_PROMPT
        if args:
            prompt += f'\n\n## Additional context\n\n{args}'
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='remember',
        description='Review auto-memory entries and propose promotions to CLAUDE.md or CLAUDE.local.md.',
        when_to_use='Use when the user wants to review, organize, or promote their auto-memory entries.',
        user_invocable=True,
        is_enabled=is_auto_memory_enabled,
        get_prompt_for_command=get_prompt,
    ))


def register_simplify_skill() -> None:
    """Register the simplify skill."""

    SIMPLIFY_PROMPT = """# Simplify: Code Review and Cleanup

Review all changed files for reuse, quality, and efficiency. Fix any issues found.

## Phase 1: Identify Changes

Run `git diff` (or `git diff HEAD` if staged) to see what changed.

## Phase 2: Launch Three Review Agents in Parallel

### Agent 1: Code Reuse Review
- Search for existing utilities that could replace newly written code
- Flag any new function that duplicates existing functionality
- Flag inline logic that could use an existing utility

### Agent 2: Code Quality Review
- Redundant state or cached values that could be derived
- Parameter sprawl
- Copy-paste with slight variation
- Leaky abstractions
- Stringly-typed code
- Unnecessary comments

### Agent 3: Efficiency Review
- Unnecessary work or redundant computations
- Missed concurrency
- Hot-path bloat
- Unnecessary existence checks
- Memory issues

## Phase 3: Fix Issues

Wait for all agents to complete. Fix each issue directly.
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = SIMPLIFY_PROMPT
        if args:
            prompt += f'\n\n## Additional Focus\n\n{args}'
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='simplify',
        description='Review changed code for reuse, quality, and efficiency, then fix issues.',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_batch_skill() -> None:
    """Register the batch skill."""

    DEFAULT_INTERVAL = '10m'

    WORKER_INSTRUCTIONS = """After you finish implementing the change:
1. Simplify - review and clean up changes
2. Run unit tests - fix if they fail
3. Test end-to-end
4. Commit and push - create a PR
5. Report - End with `PR: <url>` or `PR: none — <reason>`
"""

    def build_prompt(instruction: str) -> str:
        return f"""# Batch: Parallel Work Orchestration

You are orchestrating a large, parallelizable change across this codebase.

## User Instruction

{instruction}

## Phase 1: Research and Plan (Plan Mode)

1. **Understand the scope** - Launch subagents to research what this instruction touches
2. **Decompose into independent units** - 5-30 self-contained units
3. **Determine the e2e test recipe** - How to verify the change works
4. **Write the plan** - Include summary, work units, e2e recipe, worker instructions
5. Exit plan mode for approval

## Phase 2: Spawn Workers

Spawn background agents in isolated git worktrees. Each prompt must be fully self-contained.

## Phase 3: Track Progress

Render status table and update as agents complete.
"""

    MISSING_INSTRUCTION = """Provide an instruction describing the batch change you want to make.

Examples:
  /batch migrate from react to vue
  /batch replace all uses of lodash with native equivalents"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        instruction = args.strip()
        if not instruction:
            return [{'type': 'text', 'text': MISSING_INSTRUCTION}]
        return [{'type': 'text', 'text': build_prompt(instruction)}]

    register_bundled_skill(BundledSkillDefinition(
        name='batch',
        description='Research and plan a large-scale change, then execute in parallel across 5-30 worktree agents.',
        when_to_use='Use when the user wants to make a sweeping, mechanical change across many files.',
        argument_hint='<instruction>',
        user_invocable=True,
        disable_model_invocation=True,
        get_prompt_for_command=get_prompt,
    ))


def register_stuck_skill() -> None:
    """Register the stuck skill (ANT-only)."""
    if not is_ant_user():
        return

    STUCK_PROMPT = """# /stuck — diagnose frozen/slow Claude Code sessions

The user thinks another Claude Code session on this machine is frozen, stuck, or slow.

## What to look for

- **High CPU (≥90%) sustained** - likely infinite loop
- **Process state D** - uninterruptible sleep, I/O hang
- **Process state T** - stopped (Ctrl+Z)
- **Process state Z** - zombie
- **Very high RSS (≥4GB)** - memory leak
- **Stuck child process** - hung git/node/etc

## Investigation steps

1. List all Claude Code processes:
   `ps -axo pid=,pcpu=,rss=,etime=,state=,comm= | grep -E '(claude|cli)'`

2. For suspicious processes:
   - Child processes: `pgrep -lP <pid>`
   - If high CPU: sample again after 1-2s
   - Check debug log if available

## Report

Only post if something stuck. If healthy, tell user directly.
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = STUCK_PROMPT
        if args:
            prompt += f'\n\n## User-provided context\n\n{args}'
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='stuck',
        description='[ANT-ONLY] Investigate frozen/stuck/slow Claude Code sessions.',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_loop_skill() -> None:
    """Register the loop skill."""

    DEFAULT_INTERVAL = '10m'

    USAGE_MESSAGE = f"""Usage: /loop [interval] <prompt>

Run a prompt or slash command on a recurring interval.

Intervals: Ns, Nm, Nh, Nd (e.g. 5m, 30m, 2h, 1d).
If no interval specified, defaults to {DEFAULT_INTERVAL}.

Examples:
  /loop 5m /babysit-prs
  /loop 30m check the deploy
  /loop check the deploy (defaults to {DEFAULT_INTERVAL})
"""

    def build_prompt(args: str) -> str:
        trimmed = args.strip()
        if not trimmed:
            return USAGE_MESSAGE

        # Parse interval from input
        interval = DEFAULT_INTERVAL
        prompt = trimmed

        # Rule 1: Leading token matches ^\d+[smhd]$
        match = re.match(r'^(\d+[smhd])\s+(.*)$', trimmed)
        if match:
            interval = match.group(1)
            prompt = match.group(2)
        else:
            # Rule 2: Trailing "every" clause
            every_match = re.search(r'\s+every\s+(\d+)\s*(m(?:inute)?s?|h(?:our)?s?|d(?:ays?)?)$', trimmed, re.IGNORECASE)
            if every_match:
                num = every_match.group(1)
                unit = every_match.group(2).lower()
                if unit.startswith('m') and 'inute' not in unit:
                    interval = f'{num}s'
                elif unit.startswith('m'):
                    interval = f'{num}m'
                elif unit.startswith('h'):
                    interval = f'{num}h'
                else:
                    interval = f'{num}d'
                prompt = re.sub(r'\s+every\s+\d+\s*[smhdays]+\s*$', '', trimmed, flags=re.IGNORECASE).strip()

        return f"""# /loop — schedule a recurring prompt

## Parsed
- Interval: {interval}
- Prompt: {prompt}

## Action
1. Call CronCreate with the interval and prompt
2. Confirm what's scheduled, the cron expression, and how to cancel
3. Execute the prompt immediately

## Input
{args}
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        trimmed = args.strip()
        if not trimmed:
            return [{'type': 'text', 'text': USAGE_MESSAGE}]
        return [{'type': 'text', 'text': build_prompt(trimmed)}]

    # Note: is_enabled would check isKairosCronEnabled in full implementation
    register_bundled_skill(BundledSkillDefinition(
        name='loop',
        description='Run a prompt or slash command on a recurring interval.',
        when_to_use='When the user wants to set up a recurring task or poll for status.',
        argument_hint='[interval] <prompt>',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_schedule_remote_agents_skill() -> None:
    """Register the schedule skill for remote agents."""

    SCHEDULE_PROMPT = """# Schedule Remote Agents

You are helping the user schedule, update, list, or run **remote** Claude Code agents.

## What You Can Do
- list - list all triggers
- get - fetch one trigger
- create - create a trigger
- update - partial update
- run - run a trigger now

## Create body shape
```json
{
  "name": "AGENT_NAME",
  "cron_expression": "CRON_EXPR",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "ENVIRONMENT_ID",
      "session_context": {
        "model": "claude-sonnet-4-6",
        "sources": [{"git_repository": {"url": "https://github.com/ORG/REPO"}}],
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]
      }
    }
  }
}
```

## Cron Expression Examples
- `0 9 * * 1-5` — Every weekday at 9am UTC
- `0 */2 * * *` — Every 2 hours
- `0 0 * * *` — Daily at midnight UTC

Minimum interval is 1 hour.

## Workflow

### CREATE
1. Understand the goal
2. Craft the prompt
3. Set the schedule
4. Choose the model
5. Review and confirm
6. Create via RemoteTriggerTool

### UPDATE
1. List triggers first
2. Ask what to change
3. Confirm and update

### LIST
1. Fetch and display
2. Show: name, schedule, enabled, next run

### RUN NOW
1. List if not specified
2. Confirm
3. Execute
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = SCHEDULE_PROMPT
        if args:
            prompt += f'\n## User Request\n\n{args}'
        return [{'type': 'text', 'text': prompt}]

    # Note: is_enabled would check feature flags in full implementation
    register_bundled_skill(BundledSkillDefinition(
        name='schedule',
        description='Create, update, list, or run scheduled remote agents.',
        when_to_use='When the user wants to schedule a recurring remote agent or manage triggers.',
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def register_claude_api_skill() -> None:
    """Register the claude-api skill (BUILDING_CLAUDE_APPS feature)."""
    # Note: In full implementation, would lazy-load content from claudeApiContent
    # and detect language from project files

    PROMPT = """# Claude API Skill

Build apps with the Claude API or Anthropic SDK.

## Your Task
Help the user build applications using the Claude API.

## Detecting Language
Look for:
- Python: .py, requirements.txt, pyproject.toml
- TypeScript: .ts, .tsx, package.json
- Java: .java, pom.xml, build.gradle
- Go: .go, go.mod
- Ruby: .rb, Gemfile

## Common Tasks
- Single classification/summarization/extraction → use messages API
- Chat UI with streaming → use streaming responses
- Long conversations → use compaction strategies
- Prompt caching → implement cache controls
- Function calling → use tools
- Batch processing → use batch API
"""

    def get_prompt(args: str = '') -> list[dict[str, Any]]:
        prompt = PROMPT
        # Note: In full implementation, would detect language and include relevant docs
        if args:
            prompt += f'\n\n## User Request\n\n{args}'
        return [{'type': 'text', 'text': prompt}]

    register_bundled_skill(BundledSkillDefinition(
        name='claude-api',
        description='Build apps with the Claude API or Anthropic SDK. Trigger when user asks about Claude API, Anthropic SDKs, or Agent SDK.',
        allowed_tools=['Read', 'Grep', 'Glob', 'WebFetch'],
        user_invocable=True,
        get_prompt_for_command=get_prompt,
    ))


def init_bundled_skills() -> None:
    """Initialize all bundled skills."""
    register_update_config_skill()
    register_keybindings_skill()
    register_verify_skill()
    register_debug_skill()
    register_lorem_ipsum_skill()
    register_skillify_skill()
    register_remember_skill()
    register_simplify_skill()
    register_batch_skill()
    register_stuck_skill()
    register_loop_skill()
    register_schedule_remote_agents_skill()
    register_claude_api_skill()


# Auto-initialize on import
init_bundled_skills()


def generate_lorem_ipsum(target_tokens: int) -> str:
    """Generate lorem ipsum text for given token count.

    Args:
        target_tokens: Number of tokens to generate (capped at 500,000)

    Returns:
        Generated lorem ipsum text
    """
    # Cap at 500k tokens for safety
    target_tokens = min(target_tokens, 500_000)

    tokens = 0
    result = ''

    while tokens < target_tokens:
        sentence_length = 10 + int(random.random() * 11)
        words_in_sentence = 0

        for i in range(sentence_length):
            if tokens >= target_tokens:
                break

            word = ONE_TOKEN_WORDS[int(random.random() * len(ONE_TOKEN_WORDS))]
            result += word
            tokens += 1
            words_in_sentence += 1

            if i == sentence_length - 1 or tokens >= target_tokens:
                result += '. '
            else:
                result += ' '

        if words_in_sentence > 0 and random.random() < 0.2 and tokens < target_tokens:
            result += '\n\n'

    return result.strip()


__all__ = [
    'BundledSkillDefinition',
    'BUNDLED_SKILLS',
    'register_bundled_skill',
    'get_bundled_skill',
    'get_all_bundled_skills',
    'init_bundled_skills',
    'generate_lorem_ipsum',
    'ONE_TOKEN_WORDS',
]