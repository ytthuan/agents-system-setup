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
| GitHub Copilot CLI | `task` tool, `agent_type: "explore"` | explore | runtime-selected; read-only profile | Copilot CLI tool definition (no canonical public URL; defined by Copilot CLI runtime) |
| GitHub Copilot CLI | `task` tool, `agent_type: "task"` | task | runtime-selected; brief summary on success, full output on failure | Copilot CLI tool definition (no canonical public URL; defined by Copilot CLI runtime) |
| Claude Code | `Explore` built-in subagent | explore | runtime-selected; read-only profile | `https://docs.claude.com/en/docs/claude-code/sub-agents` |
| Claude Code | `general-purpose` built-in subagent | task | Inherits parent context and tools for multi-step work | `https://docs.claude.com/en/docs/claude-code/sub-agents` |
| OpenCode | `explore` subagent | explore | Read-only | `https://opencode.ai/docs/agents/` |
| OpenCode | `general` subagent | task | Full tool access except `todo` | `https://opencode.ai/docs/agents/` |
| OpenAI Codex (CLI + App) | `explorer` built-in | explore | Read-heavy built-in | `https://developers.openai.com/codex/subagents` |
| OpenAI Codex (CLI + App) | none documented | task | n/a | `https://developers.openai.com/codex/subagents` |
| Gemini CLI | `codebase_investigator` built-in subagent | explore | Read-only codebase investigation | `https://geminicli.com/docs/core/subagents/` |
| Gemini CLI | none documented | task | n/a | `https://geminicli.com/docs/core/subagents/` |

## Routing decision rules

Choose direct host work first. Recommend explore-class delegation only when
broad reconnaissance is substantial enough that a separate context materially
helps. Repository-size signals may inform the decision but are not mandatory
thresholds and do not force tool invocation.

Recommend task-class delegation for verbose, one-off command execution where the
host only needs a success/failure summary and the full output only on failure.
Examples include ad-hoc `npm test`, `cargo build`, `pip install`,
`tsc --noEmit`, or `eslint .` checks outside a required gate.

**Boundary rule:** task-class built-in output is ad-hoc `non-gate evidence`
unless the built-in was explicitly assigned through the established owning
gate workflow with the same scope, independence, and evidence contract. Native
routing never silently changes gate meaning or ownership. Review remains
independent of the writer.

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
- **Sandbox and permission notes:** use its documented read-only profile and
  let the runtime choose among models allowed by the active policy.

Task-class built-in:

- **Name:** `general-purpose`.
- **Invocation:** ask Claude to use `general-purpose` for multi-step command or
  execution-heavy work when only a concise result should return to the host.
- **Sandbox and permission notes:** it inherits parent tools. Inherited model
  or tools are not assumed cheap or safe; the host applies adaptive delegation
  and established gate ownership.

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

All root profiles use the same short block, no more than five physical lines,
with the stable anchor. Full runtime mechanics remain locally available in this
reference and `task-delegation`; do not use a remote-only pointer for required
context.

```markdown
<!-- agents-system-setup:host-builtins-routing -->
### Native Runtime Agents
**Audience:** host-orchestrator
Use a runtime built-in only when its separate context or execution summary materially helps; no worker count or forced invocation applies. Load `task-delegation` for the current per-runtime routing mechanics.
Explore/task-class results are ad-hoc `non-gate evidence` unless assigned through the established owning-gate workflow; workers never re-delegate.
```

## Anti-patterns

- Treating an ad-hoc task-class invocation as Build Gate evidence without
  assigning it through the established owning-gate workflow.
- Telling Codex to use `reviewer` for arbitrary command execution. The Codex
  `reviewer` built-in is review-only.
- Telling Gemini subagents to delegate command execution to other subagents.
  Gemini fan-out stays in the root session.
- Adding native built-in routing without updating OpenCode `permission.task`
  allow entries for `explore` and `general`.
- Adding a delegation hint inside subagent templates. That violates hard rule
  #36: subagents are executors and must return to the orchestrator when scope
  exceeds their surface.
- Requiring a minimum specialist count before using one helpful built-in.
- Invoking a built-in merely because it is available.
