# Host Builtins Routing

Native Runtime Agents are host-provided built-in subagents that a generated
agent system can ask the host orchestrator to use: `explore`-class agents for
read-only reconnaissance, and `task`-class agents for verbose command execution
where the host only needs a compact success/failure result. This reference is
for systems the plugin generates; the plugin's own recon delegation is covered
separately by [explorer-agents](./explorer-agents.md).

## Source citations table

| Runtime | Built-in name | Class | Model | Documentation URL |
|---|---|---|---|---|
| GitHub Copilot CLI | `task` tool, `agent_type: "explore"` | explore | Haiku, read-only | Copilot CLI tool definition (no canonical public URL; defined by Copilot CLI runtime) |
| GitHub Copilot CLI | `task` tool, `agent_type: "task"` | task | Haiku; brief summary on success, full output on failure | Copilot CLI tool definition (no canonical public URL; defined by Copilot CLI runtime) |
| Claude Code | `Explore` built-in subagent | explore | Haiku, read-only | `https://docs.claude.com/en/docs/claude-code/sub-agents` |
| Claude Code | `general-purpose` built-in subagent | task | Inherits parent context and tools for multi-step work | `https://docs.claude.com/en/docs/claude-code/sub-agents` |
| OpenCode | `explore` subagent | explore | Read-only | `https://opencode.ai/docs/agents/` |
| OpenCode | `general` subagent | task | Full tool access except `todo` | `https://opencode.ai/docs/agents/` |
| OpenAI Codex (CLI + App) | `explorer` built-in | explore | Read-heavy built-in | `https://developers.openai.com/codex/subagents` |
| OpenAI Codex (CLI + App) | none documented | task | n/a | `https://developers.openai.com/codex/subagents` |
| Gemini CLI | `codebase_investigator` built-in subagent | explore | Read-only codebase investigation | `https://geminicli.com/docs/core/subagents/` |
| Gemini CLI | none documented | task | n/a | `https://geminicli.com/docs/core/subagents/` |

## Routing decision rules

Recommend explore-class delegation when broad reconnaissance would consume the
main host context or benefits from parallel reading. Use the same trigger as the
plugin's own explorer routing: `source_files > 50` OR `top_level_dirs > 8` OR
`frameworks_detected > 3` OR `recon_threads_requested > 2`.

Recommend task-class delegation for verbose, one-off command execution where the
host only needs a success/failure summary and the full output only on failure.
Examples include ad-hoc `npm test`, `cargo build`, `pip install`,
`tsc --noEmit`, or `eslint .` checks outside a required gate.

**Boundary rule:** Build Gate evidence MUST stay with `@build-runner`, tester,
e2e, and `@change-validator` owners. Native task-class built-ins are the
execution substrate for ad-hoc non-gate checks only. Label their output
`non-gate evidence`; it does NOT satisfy Build Gate evidence requirements from
[sdlc-build-gate](./sdlc-build-gate.md).

**Subagent rule:** Subagents never re-delegate to native built-ins. If a
subagent's task needs host-level command execution outside its allowed surface,
it returns `return-to-orchestrator` with the command and evidence shape it
needs. The orchestrator then decides between a custom subagent and a native
built-in.

## Per-runtime routing inventory

### GitHub Copilot CLI

Source: Copilot CLI runtime tool definition; no canonical public URL.

Explore-class built-in:

- **Name:** `task` tool with `agent_type: "explore"`.
- **Invocation:** host session launches `task(agent_type: "explore", prompt:
  "...")` for read-only reconnaissance.
- **Sandbox and permission notes:** the built-in is read-only and optimized for
  fast codebase exploration in a separate context window.

Task-class built-in:

- **Name:** `task` tool with `agent_type: "task"`.
- **Invocation:** host session launches `task(agent_type: "task", prompt:
  "Run <command> and report success/failure; include full output only on
  failure.")`.
- **Sandbox and permission notes:** use only for ad-hoc non-gate checks. Gate
  checks still route through generated owners such as `@build-runner`.

### Claude Code

Source: `https://docs.claude.com/en/docs/claude-code/sub-agents`.

Explore-class built-in:

- **Name:** `Explore`.
- **Invocation:** let Claude auto-delegate, or explicitly ask `Explore` to
  inspect a bounded read-only concern.
- **Sandbox and permission notes:** the built-in is Haiku-backed and read-only,
  matching reconnaissance work.

Task-class built-in:

- **Name:** `general-purpose`.
- **Invocation:** ask Claude to use `general-purpose` for multi-step command or
  execution-heavy work when only a concise result should return to the host.
- **Sandbox and permission notes:** it inherits parent tools; generated systems
  still keep Build Gate ownership with named custom agents.

### OpenCode

Source: `https://opencode.ai/docs/agents/`.

Explore-class built-in:

- **Name:** `explore`.
- **Invocation:** `@explore <bounded recon prompt>` from the host orchestrator.
- **Sandbox and permission notes:** read-only; intended for investigation, not
  edits.

Task-class built-in:

- **Name:** `general`.
- **Invocation:** `@general <command-heavy prompt>` from the host orchestrator.
- **Sandbox and permission notes:** full tool access except `todo`; use only for
  ad-hoc non-gate checks.

When this routing is emitted, `opencode.json` `permission.task` MUST allow
`explore` and `general`; otherwise routing is advisory-only and the output
contract records `host_builtins_routing: declined`.

### OpenAI Codex CLI and App

Source: `https://developers.openai.com/codex/subagents`.

Explore-class built-in:

- **Name:** `explorer`.
- **Invocation:** the host asks Codex orchestration to spawn `explorer` for
  bounded read-only reconnaissance.
- **Sandbox and permission notes:** use the normal Codex subagent depth and
  thread limits recorded in `.codex/config.toml`.

Task-class built-in:

- **Name:** none documented.
- **Invocation:** Codex has no documented generic task-class built-in.
  `reviewer` is review-only; do NOT use it as a task-class substitute.
- **Fallback:** for command execution, the host spawns a custom worker subagent
  (`sandbox_mode = "workspace-write"` with explicit tool allowlist), OR routes
  to generated `@build-runner`, OR runs commands in the root session.

### Gemini CLI

Source: `https://geminicli.com/docs/core/subagents/`.

Explore-class built-in:

- **Name:** `codebase_investigator`.
- **Invocation:** `@codebase_investigator <bounded recon prompt>` from the root
  Gemini session, or root-session auto-delegation for complex codebase
  questions.
- **Sandbox and permission notes:** read-only investigation happens in a separate
  context window.

Task-class built-in:

- **Name:** none documented.
- **Invocation:** Gemini has no documented task-class built-in.
- **Fallback:** the root Gemini session runs command-heavy work directly or
  delegates to generated `@build-runner` / tester subagents. Gemini subagents
  must not call other subagents; all fan-out stays in the root session.

## AGENTS.md emission shape

Render this subsection under `## Orchestration Operating Model`, near
`### Platform-native delegation`. Preserve the HTML anchor exactly.

```markdown
<!-- agents-system-setup:host-builtins-routing -->

### Native Runtime Agents

**Audience:** host-orchestrator

| Runtime | Explore-class (broad recon) | Task-class (verbose command execution) |
|---|---|---|
| GitHub Copilot CLI | `task` tool, `agent_type: "explore"` | `task` tool, `agent_type: "task"` |
| Claude Code | `Explore` built-in subagent | `general-purpose` built-in subagent |
| OpenCode | `@explore` subagent | `@general` subagent |
| OpenAI Codex (CLI + App) | `explorer` built-in | No task-class built-in; use custom worker / `@build-runner` / root session |
| Gemini CLI | `@codebase_investigator` | No task-class built-in; root session / `@build-runner` / tester subagents |
```

Balanced and Full profiles include the table plus the boundary and subagent
rules. Compact profile emits a one- or two-line summary with a link back to this
reference. Single-agent setups omit the subsection entirely.

## Anti-patterns

- Routing a Build Gate-required check through a native task-class built-in. Build,
  unit test, e2e, code review, change bug hunt, and validation evidence require
  the named owner.
- Telling Codex to use `reviewer` for arbitrary command execution. The Codex
  `reviewer` built-in is review-only.
- Telling Gemini subagents to delegate command execution to other subagents.
  Gemini fan-out stays in the root session.
- Adding native built-in routing without updating OpenCode `permission.task`
  allow entries for `explore` and `general`.
- Adding a delegation hint inside subagent templates. That violates hard rule
  #36: subagents are executors and must return to the orchestrator when scope
  exceeds their surface.
