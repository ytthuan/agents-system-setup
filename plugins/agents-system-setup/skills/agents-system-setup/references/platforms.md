# Multi-Platform Emission Reference

This skill targets five agent runtimes. The user picks one or more in **Phase
0** of the interview; the generator loops over the selection. Runtime drift and
supported-surface decisions are tracked in
[runtime-updates](./runtime-updates.md). Fresh project-memory setup follows
[native initialization](./native-initialization.md): initialize only through
the active harness after tracking/file-plan approval, then synthesize one
compact canonical `AGENTS.md`.

## Supported Platforms

| Platform | Docs |
|---|---|
| **Copilot CLI** | https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents |
| **Claude Code** | https://docs.anthropic.com/en/docs/claude-code/sub-agents |
| **OpenCode** | https://opencode.ai/docs/agents/ · https://opencode.ai/docs/mcp-servers/ |
| **OpenAI Codex (CLI + App)** | https://github.com/openai/codex · https://agents.md · https://developers.openai.com/codex/subagents |
| **Gemini CLI** | https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md · https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md |

## Path / Format Matrix

| Artifact | Copilot CLI | Claude Code | OpenCode | OpenAI Codex (CLI + App) | Gemini CLI |
|---|---|---|---|---|---|
| Agents | Emit `.github/agents/<name>.agent.md`; also recognize `.github/agents/<name>.md` as an upstream docs drift/import signal | `.claude/agents/<name>.md` | Markdown default: `.opencode/agents/<name>.md`; JSON import/update surface: `opencode.json` top-level `agent` | orchestrator + project rules in `AGENTS.md`; **specialized subagents in `.codex/agents/<name>.toml`** (project) or `~/.codex/agents/` (user) | `.gemini/agents/<name>.md` (project local subagent) or `~/.gemini/agents/<name>.md` (user); extension `agents/*.md` is import/package surface |
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md`; keep separate from commands; gated by `permission.skill` | `.agents/skills/<name>/SKILL.md` in the project or an ancestor, `~/.agents/skills/<name>/SKILL.md` for the user, `/etc/codex/skills/<name>/SKILL.md` for admins; `.codex/skills/` is legacy migration input, not the current emitter | `.gemini/skills/<name>/SKILL.md` (project) or `~/.gemini/skills/<name>/SKILL.md` (user); `.agents/skills/<name>/SKILL.md` also recognized; extension-packaged skills also supported; activation is model-side via skill loading; managed with `/skills`; no `$skill` or `/<skill>` invocation |
| MCP servers | `.mcp.json` (root) | `.mcp.json` (root, shared with Copilot) | `opencode.json` › `"mcp": { ... }` | `.mcp.json` (root, shared) | per-agent `mcp_servers:` in `.gemini/agents/*.md`; extension manifests use `mcpServers`; all MCP writes are approval-gated |
| Hooks | `.github/hooks/*.json` | `.claude/settings.json` › `"hooks"` | `.opencode/hooks/` | not supported | native `settings.json` hooks at project / user / system scope; extension `hooks/hooks.json` when packaging; not extension-only |
| Commands | plugin `commands/<cmd>.md` under plugin root | plugin `commands/<cmd>.md` supported for slash commands (not legacy); project commands at `.claude/commands/<cmd>.md` | `.opencode/commands/<name>.md` or `command` config key; invoked as `/<name>`; `$ARGUMENTS`/`$1` are body placeholders, not invocation syntax; keep separate from skills | not a standard surface | Gemini extensions can bundle `commands/*.md`; no native project command surface |
| Human input | Session `ask_user`; disabled by `--no-ask-user`; not a custom-agent `tools:` alias | `AskUserQuestion` tool; include in restrictive `tools:` only for ask-capable agents | `question` tool, granted with nested `permission: { question: allow }` | `request_user_input` in Plan mode only; no TOML field | `ask_user` tool; valid in `tools:` allowlists for interactive agents |
| Project memory | `AGENTS.md` (root, canonical project memory); `.github/copilot-instructions.md` only for an approved compatibility/override need | Thin `CLAUDE.md` adapter with `@AGENTS.md`, plus Claude-only overrides | `AGENTS.md` (native) | `AGENTS.md` (native — primary consumer in Codex CLI + App artifact flows) | Thin `GEMINI.md` adapter with `@AGENTS.md`, plus Gemini-only overrides |
| Personal memory | `~/.copilot/AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.config/opencode/AGENTS.md` | `~/.codex/AGENTS.md` | `~/.gemini/GEMINI.md` plus `~/.gemini/agents/` |
| Native durable learning | Copilot Memory public preview: transparent server-side durable repo memory; plugin-managed learning remains complementary | `memory` set to `user`, `project`, or `local` for project/user/session agents; plugin agents support memory but not `hooks`, `mcpServers`, or `permissionMode` | No durable auto-learning beyond AGENTS.md, skills, compaction, and plugin patterns | Memories feature via `[features] memories = true` and `~/.codex/memories/`; off by default/region-limited; do not emit `memory` in agent TOML | `save_memory`, `GEMINI.md`, `/memory`, and experimental `autoMemory`; skills use `activate_skill` |

### Skill loading and child-context rule

`task-delegation`, `code-change-build-gate`, and other applicable host skills
are emitted at each selected runtime's current skills path. `task-handoff` and
`host-handoff` are legacy migration/import names only. Auto-load and
child-context semantics differ:

| Runtime | Skill auto-load behavior | Subagent template policy |
|---|---|---|
| Copilot CLI | Skills surface via slash discovery; not guaranteed to be in subagent context | Keep compact inline Acceptance + Reporting (not just 12-field guard); skill is the expanded procedure |
| Claude Code | Project skills available via `/skills`; loaded on demand | Keep compact inline Acceptance + Reporting; skill is the expanded procedure |
| OpenCode | Skills are loaded through the `skill` tool, gated by `permission.skill` | Keep compact inline Acceptance + Reporting; skill is the expanded procedure |
| OpenAI Codex (CLI + App) | Skill loader can activate skills; users can select with `$skill-name` or browse with `/skills` | Keep the fail-closed intake/reporting minimum in `developer_instructions`; host discovery or loading does not prove the child received the skill body |
| Gemini CLI | Activation is model-side via skill loading; no guarantee subagent context loads the skill | Keep compact inline Acceptance + Reporting; skill is the expanded procedure |

**Rule:** every subagent keeps a compact fail-closed Acceptance Checklist and
Reporting Template. The host records whether `task-delegation` was discoverable
and host-loaded (`Skills Referenced: task-delegation loaded=true|false`)
separately from whether the child received its body. Pass the needed excerpt or
use a supported child preload/attachment mechanism; a pointer alone is never
evidence that the child loaded it. Missing or denied required skill context
blocks the affected gated action.

> **Operational state directory.** Never write `agents/`, `skills/`, `hooks/`, `commands/`, `prompts/`, or `plugins/` subtrees inside `.agents-system-setup/`. Runtimes do not load artifacts from there; existing misroutes go through [misplaced-artifacts-migration](./misplaced-artifacts-migration.md).
>
> **Instruction memory adapter rule.** `AGENTS.md` is the canonical
> cross-runtime memory. Prefer small `@AGENTS.md` adapters for Claude and
> Gemini rather than symlinks or copies. Copilot, Codex, and OpenCode consume
> `AGENTS.md` natively, so do not add redundant adapters. Audit the whole load
> graph: native loaders can combine multiple files/imports, and imports or
> audience tags are not lazy context savings.

- **Native explorer agents** for codebase recon: every supported runtime ships a built-in explorer subagent (Copilot CLI `task/explore`, Claude Code `Explore`, OpenCode `explore`, Codex `explorer`, Gemini CLI `codebase_investigator`). See [explorer-agents](./explorer-agents.md) for the per-runtime mapping, the 5-thread parallel recon recipe, and the trigger heuristic (`source_files > 50` OR `top_level_dirs > 8` OR `frameworks_detected > 3` OR `recon_threads_requested > 2`).

## Agent Frontmatter — per platform

### Copilot CLI (`.agent.md`)

The emitter writes `.github/agents/<name>.agent.md`. GitHub concept docs also mention `.github/agents/<name>.md`; treat that as a detection/import signal until the authoritative CLI behavior supports switching the emitter.

```yaml
---
name: planner
description: 'Use when ...'
model: claude-sonnet-4.6                               # optional
tools: [vscode, execute, read, agent, edit, search, todo]  # Standard Tool Profile (recommended default)
mcp-servers:                                           # optional, hyphenated key
  github: { command: npx, args: [...], env: {...} }
---
```

Copilot source-backed runtime notes:
- Custom agents are agent profiles. The main Copilot agent can run them as subagents in a separate context window, automatically by description, explicitly by `/agent`, by prompt mention, or programmatically with `copilot --agent <name> --prompt ...`.
- Prefer public tool aliases in generated `tools:`: `vscode`, `execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`. Compatible aliases such as `Bash`, `Read`, `Grep`, `Glob`, `Task`, and MCP-prefixed names are import-safe, but emit public aliases to keep profiles portable across Copilot surfaces.
- Human input is the session-level `ask_user` tool; `--no-ask-user` disables it. Do not add `ask_user` to custom-agent `tools:` because it is not in the documented alias table. Subagents return `question_request` to the orchestrator/session when they need clarification.
- Fresh memory initialization supports interactive `/init` and terminal
  `copilot init`; GitHub documents `.github/copilot-instructions.md` as the
  default output. The plugin instead prefers interactive
  `/init generate AGENTS.md at root instead of .github/copilot-instructions.md`.
  This is a requested target, not a guaranteed filename override or a shell
  argument. Inspect observed output and ask only if unsupported or conflicting.
- Copilot Memory is a public-preview, transparent server-side durable repo memory surface. Treat plugin-managed Learning Check artifacts as complementary, explicit project policy and audit records.
- `vscode` exposes the VS Code chat-host tool set (e.g., `vscode/extensions`, `vscode/runCommands`) when the agent runs inside VS Code Chat. Copilot CLI and other surfaces ignore it harmlessly per the documented "All unrecognized tool names are ignored" rule, so it is safe to ship as a baseline.
- `agent` / `custom-agent` / `Task` enables one custom agent to invoke another. Grant it only to orchestrator-style agents; read-only reviewers should not be able to spawn broad workers.
- Delegate only when a specialist or independent context materially helps.
  `/fleet` is an optional parent-orchestrated mode for substantial independent
  CLI batches; generated files must not depend on it or force fan-out.
- If `mcp-servers:` appears in frontmatter, the Phase 3.5 MCP approval gate must have rendered and approved it first, and the rendered agent must carry an `agents-system-setup:mcp-approved` marker.

#### Copilot CLI Standard Tool Profiles

> **Canonical tool list:** `assets/tool-catalog.json` (see [tool-catalog](./tool-catalog.md) for the human view). The tables below are an emit-time convenience; the JSON catalog is authoritative.

Generated Copilot CLI agents apply one of these named profiles (selected per role at emit time; user can override via the interview):

| Profile | `tools:` allowlist | Use for |
|---|---|---|
| `standard` (default for orchestrator + edit-capable subagents) | `[vscode, execute, read, agent, edit, search, todo]` | Orchestrator, implementer, runner, edit-capable specialist |
| `read-only` (default for reviewers/auditors) | `[read, search]` | `@reviewer`, `@security`, `@architecture`, `@docs-reviewer`, any agent with empty `Owns:` paths |
| `runner` (no edit, can shell + report) | `[execute, read, search, todo]` | `@tester`, CI/release helper |
| `research` (read + web + todo) | `[read, search, web, todo]` | Research/documentation gatherers |
| `inherit` (omit `tools:`) | (omitted) | Explicit user opt-out — agent receives parent's full toolbelt |

Role → Profile mapping (case-insensitive substring on the agent name or role) used during emission:

| Role pattern | Profile |
|---|---|
| `orchestrator`, `planner`, `coordinator` | `standard` |
| `reviewer`, `auditor`, `security`, `architect`, `governance` | `read-only` |
| `tester`, `qa`, `runner`, `release` | `runner` |
| `research`, `docs`, `discovery`, `intake` | `research` |
| anything else with non-empty `Owned paths` | `standard` |
| anything else with empty `Owned paths` | `read-only` |

Sources:
- Copilot custom-agent config reference: <https://docs.github.com/en/copilot/reference/custom-agents-configuration> (tool aliases + "all unrecognized tool names are ignored").
- VS Code custom agents (`.github/agents/*.agent.md` is shared with Copilot CLI): <https://code.visualstudio.com/docs/copilot/customization/custom-agents>.

### Claude Code (`.md` under `.claude/agents/`)
Only `name` + `description` required. Defaults: `model: inherit`, all tools inherited from parent. Source: https://docs.claude.com/en/docs/claude-code/sub-agents
```yaml
---
name: planner                                  # REQUIRED — lowercase + hyphens, unique, matches filename
description: Use when ...                      # REQUIRED — drives delegation
tools: Read, Grep, Glob, Bash, AskUserQuestion # optional comma-string allowlist; omit = inherit all
disallowedTools: Write, Edit     # optional denylist (applied before `tools`)
model: sonnet                    # optional: sonnet | opus | haiku | <full-id> | inherit (default)
permissionMode: default          # optional: default | acceptEdits | auto | dontAsk | bypassPermissions | plan
skills: [code-review]            # optional: full skill body injected (subagents do NOT inherit parent skills)
mcpServers: { slack: {} }        # optional: name ref or inline config
isolation: worktree              # optional: isolated git worktree copy
color: blue                      # optional UI color
# Also: maxTurns, hooks, memory (user|project|local), background, effort, initialPrompt
---
```
> Tool names are Claude's canonical names (`Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `Agent`, `WebFetch`). Do **not** copy Copilot tool names verbatim. Scope precedence: managed settings > `--agents` CLI > project (`.claude/agents/`) > user (`~/.claude/agents/`) > plugin.
>
> Project/user/session agents and plugin-shipped agents are not the same schema surface. Project/user/session agents may use richer fields such as `mcpServers`, `hooks`, and `permissionMode`; plugin-shipped agents support `memory` but must not rely on unsupported fields such as `hooks`, `mcpServers`, or `permissionMode`.
>
> Use `AskUserQuestion` only when a restrictive `tools:` allowlist would otherwise prevent an interactive agent that is expected to ask the user. If it is absent, the run is headless, or `background: true` is set, the subagent reports `question_request` to the orchestrator instead.
>
> **Commands vs skills:** Plugin `commands/` (under the plugin root) remain fully supported for slash commands and are not legacy. Use `commands/` for prompt-template slash commands; prefer skills for reusable multi-step workflows. Project-level slash commands live at `.claude/commands/<cmd>.md`.
>
> Distinguish three Claude primitives:
> 1. **Subagent definition** — a Markdown file or `--agents` JSON object describing a specialist.
> 2. **Tool-based subagent invocation** — Claude delegates through its `Agent` tool inside the current session; the worker reports back only to the caller and cannot recursively spawn subagents.
> 3. **Agent teams** — experimental separate Claude Code instances enabled by `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; teammates can message each other directly and use a shared task list. Emit `AGENT-TEAMS.md` only as opt-in guidance with token-cost warnings.

### OpenCode (`.md` under `.opencode/agents/` or `~/.config/opencode/agents/`)
Only `description` required. Filename = agent name. `tools:` is deprecated — prefer `permission`. Source: https://opencode.ai/docs/agents/
```yaml
---
description: Use when ...                                  # REQUIRED
mode: subagent                                             # primary | subagent | all (default: all)
model: anthropic/claude-sonnet-4-20250514                  # provider/model-id
temperature: 0.1                                           # optional
prompt: "{file:./prompts/review.txt}"                      # optional external system prompt
steps: 5                                                   # optional max agentic iterations
hidden: false                                              # hide from @ autocomplete
permission:                                                # preferred over deprecated `tools:`
  question: allow                                          # ask the user from interactive primary agents
  edit: deny                                               # allow | ask | deny
  webfetch: deny
  bash:
    "*": ask                                               # wildcard FIRST, specific after (last match wins)
    "git status *": allow
  task:                                                    # gate Task-tool subagent invocation
    "*": deny
    "code-reviewer": allow
---
```
> MCP servers live in `opencode.json` › `mcp`, NOT in agent frontmatter. Built-in primaries: `build`, `plan`. Built-in subagents: `general`, `explore`. Hidden system agents may exist for runtime internals such as compaction/title/summary. Extra top-level keys (e.g. `reasoningEffort`) pass through as provider model options.
>
> Permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `todowrite`, `webfetch`, `websearch`, `codesearch`, `lsp`, `skill`, `question`, `doom_loop`. Prefer `permission:` for new configs; `tools:` is deprecated.
>
> Human input uses the `question` tool. Grant it with nested YAML such as `permission: { question: allow }` or the block above; do not emit a literal dotted key. OpenCode has no durable auto-learning surface beyond AGENTS.md, skills, compaction, and plugin-managed patterns.
>
> Primary agents are selected directly (Tab / configured `switch_agent` keybind). Subagents are invoked automatically by primary agents or manually with `@<agent-name>`. When a subagent creates a child session, users navigate with `session_child_first`, `session_child_cycle`, `session_child_cycle_reverse`, and `session_parent`; include these as "Try it" notes, not schema fields. Gate subagent spawning with `permission.task` when an agent should only call specific workers. Generated orchestrators default to `permission.task` with `"*": deny` plus explicit roster-agent allows. If a primary intentionally has no named task allows, render `# agents-system-setup:permission-task-roster: skipped`.

#### Canonical OpenCode primary task gate

OpenCode primary agents must gate subagent spawning with a `permission.task`
mapping. The wildcard/default entry must be `deny` or `ask`; never emit
`"*": allow`.

```yaml
permission:
  question: allow
  task:
    "*": deny
    "reviewer": allow
    "tester": allow
```

Use `permission.task: { "*": ask }` only when the user explicitly approves
broad runtime-selected delegation. See the
[optional placeholder substitution table](./agent-format.md#optional-placeholder-substitution-table)
for the generated `{{OPTIONAL_PERMISSION_TASK_BLOCK}}` forms.

#### OpenCode commands

OpenCode slash commands live at `.opencode/commands/<name>.md` or are declared via the `command` key in config. They are invoked as `/<name>` at runtime. Inside the command body, `$ARGUMENTS` (or `$1`) are placeholder substitution variables — they are not part of the invocation syntax. Keep commands separate from skills: skills are loaded via the skill tool and gated by `permission.skill`; commands are prompt templates exposed as slash commands.

### OpenAI Codex CLI + App — split layout

Codex uses shared project artifacts that are compatible with both Codex CLI and Codex App surfaces where those artifacts are available. Keep **CLI-only** commands (`codex plugin marketplace add`, `/plugins`, `/agent`, `codex exec`, approval overlays) in install or "Try it" notes; generated project artifacts must not require those commands to be useful in the App.

| Surface | Applies to | Notes |
|---|---|---|
| Shared artifacts | `AGENTS.md`, `.codex/agents/*.toml`, `.codex/config.toml`, approved `.mcp.json` where supported | Source of truth for setup and replication. Keep these schema-valid and free of CLI-only requirements. |
| CLI-only UX | plugin marketplace install, `/plugins`, `/agent`, `codex exec`, interactive approval overlays | Document as CLI usage examples only. Do not claim Codex App plugin installation unless OpenAI documents it. |
| App-visible UX | subagent activity/thread visibility, display nicknames, consolidated results | Uses the same custom-agent definitions; `nickname_candidates` are presentation hints, not routing keys. |

**Project rules + orchestrator** live in compact `AGENTS.md` at the repo root
(Codex's primary input). Keep purpose, commands, ownership, essential controls,
gate triggers, and the Skills index resident. Full Capability Matrix, security
rationale, architecture detail, and review policy live at the approved local
project-policy path and load only when triggered. Do not put specialized worker
prompts in `AGENTS.md`.

**Specialized subagents** are standalone TOML files under `.codex/agents/<name>.toml` (project-scoped) or `~/.codex/agents/<name>.toml` (user-scoped). Codex loads each file as a configuration layer for the spawned session, so a custom agent file may override any setting a normal session config sets. In the CLI, switch threads with `/agent`; in the App, rely on Codex's surfaced subagent activity rather than embedding CLI-only switching requirements.

**Required fields** (per [openai docs](https://developers.openai.com/codex/subagents)):

| Field                    | Type     | Purpose                                                         |
| ------------------------ | -------- | --------------------------------------------------------------- |
| `name`                   | string   | Source of truth for the agent identity (filename is convention only). |
| `description`            | string   | Human-facing guidance for when Codex should use this agent.     |
| `developer_instructions` | string   | Core instructions defining behavior (use TOML triple-quoted string). |

**Optional fields** (inherit from parent session if omitted):
`nickname_candidates: string[]`, `model`, `model_reasoning_effort` (a nonempty
effort string advertised by the selected model/runtime), `sandbox_mode` (for
example `read-only` or `workspace-write`), `[mcp_servers.<id>]` table, and
`[[skills.config]]` array. Built-in agent names — `default`, `worker`,
`explorer` — can be overridden by a custom file using the same `name`.
`nickname_candidates` are display hints that can help in both Codex CLI and App
activity views.

```toml
name = "reviewer"
description = "Use when reviewing PRs for correctness, security, and missing tests."
model = "gpt-5.4"
# Omit both model fields unless the user explicitly pins them.
model_reasoning_effort = "high" # validate against the selected model's advertised values
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings, include reproduction steps when possible.
"""
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

**Global subagent settings** live under `[agents]` in `.codex/config.toml`:

```toml
[agents]
max_concurrent_threads_per_session = 4 # example explicit limit; preserve configured value
max_depth = 1                    # preserve recursion safety unless separately approved
job_max_runtime_seconds = 1800   # optional global job timeout
```

`agents.max_concurrent_threads_per_session` is the current concurrency setting;
recognize `max_threads` as a legacy alias during import/migration. Do not emit a
fixed value as an alleged upstream default. Preserve a user's configured limit,
and omit the setting when the plan does not approve a change.

Codex reads `.mcp.json` at repo root (shared with Copilot/Claude). Per-agent MCP servers may also be declared inline via `[mcp_servers.<id>]` in the agent's TOML.

For high-volume row-per-agent fan-out, Codex exposes `spawn_agents_on_csv`; document it as an advanced workflow rather than a default orchestrator requirement. Codex plugin manifests may also point to `skills`, `mcpServers`, `apps`, interface assets, `.app.json`, and `.mcp.json`; keep those component references in plugin docs and never auto-write MCP/app config without the approval gate.

Codex source-backed runtime notes:
- Current Codex releases enable subagent workflows by default, but Codex only
  spawns subagents when explicitly asked. Delegate only when the task benefits;
  preserve ownership and required independent review without manufacturing
  workers or maximizing concurrency.
- `request_user_input` is a Plan-mode human-input tool, not an agent TOML field. Child/default/exec flows should return `question_request` to the parent/session instead of embedding prompt-tool config in `.codex/agents/*.toml`.
- Native memories are enabled with `[features] memories = true` and stored under `~/.codex/memories/`; the feature is off by default and may be region-limited. Do not emit `memory` in agent TOML.
- Subagents inherit the current sandbox policy and live runtime approval overrides. A custom TOML `sandbox_mode` can narrow defaults, but interactive `/approvals` or `--yolo` choices still apply to spawned child sessions.
- `agents.max_concurrent_threads_per_session` caps concurrent child threads;
  `max_threads` is a legacy alias. Preserve configured concurrency and existing
  recursion safety; `agents.job_max_runtime_seconds` supplies the timeout for
  CSV jobs when configured.
- `spawn_agents_on_csv` requires an input CSV, an instruction template, and exactly one `report_agent_job_result` call per worker. Exported CSV status and metadata are an advanced batch workflow, not the default multi-agent topology.
- Plugin marketplace files can live at `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, or user-level `~/.agents/plugins/marketplace.json`; plugin roots keep `.codex-plugin/plugin.json` plus optional `skills/`, `.mcp.json`, `.app.json`, and `assets/`.
- Codex discovers skills from project/ancestor `.agents/skills/`, user
  `~/.agents/skills/`, and admin `/etc/codex/skills/`. Audit legacy
  `.codex/skills/` as migration input instead of deleting or continuing to emit
  there.

### Gemini CLI (`.md` under `.gemini/agents/` or `~/.gemini/agents/`)

Gemini CLI local subagents are Markdown files with YAML frontmatter and a body system prompt. Source: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md

```yaml
---
name: security-auditor              # REQUIRED — lowercase slug; match filename basename by convention
description: Use when reviewing code for vulnerabilities and security regressions.
kind: local                         # optional; default local
display_name: Security Auditor      # optional presentation label
tools:                              # optional allowlist; omit = inherit parent tools
  - read_file
  - grep_search
  - run_shell_command
  - ask_user
mcp_servers:                        # optional per-agent MCP; approval-gated
  docs:
    command: node
    args: ["server.js"]
model: gemini-3-flash-preview       # optional; default inherit
temperature: 0.2                    # optional; default 1
max_turns: 10                       # optional; default 30
timeout_mins: 10                    # optional; default 10
---

You are a focused security auditor...
```

Gemini source-backed runtime notes:
- The main agent can delegate automatically by description or explicitly with `@<agent-name>`. The subagent appears to the parent as a tool.
- Subagents run in isolated context loops and cannot call other subagents. Even `tools: ['*']` does not expose subagent tools to a subagent. Keep fan-out at the root/orchestrator session.
- `tools:` supports wildcards such as `*`, `mcp_*`, and `mcp_<server>_*`. Prefer narrow allowlists for reviewers and docs agents.
- Human input uses `ask_user`; include it in `tools:` only for interactive agents expected to ask. Headless agents return `question_request`.
- The docs prose may show `mcpServers`, but the local subagent loader schema validates `mcp_servers`. Emit snake_case `mcp_servers:` in `.gemini/agents/*.md`; reserve camelCase `mcpServers` for Gemini extension manifest/package surfaces and normalize imported local-agent examples with a warning.
- Remote A2A subagents (`kind: remote`, `agent_card_url`, `agent_card_json`, `auth`) are advanced/import-only; do not emit them by default.
- Gemini CLI supports native skills loaded from `.gemini/skills/<name>/SKILL.md` (project) or `~/.gemini/skills/<name>/SKILL.md` (user); `.agents/skills/<name>/SKILL.md` is also recognized. Activation is model-side via skill loading; use `/skills` to manage loaded skills. There is no `$skill` or `/<skill>` invocation syntax — skills are not slash commands.
- Gemini native memory includes `save_memory`, `GEMINI.md`, `/memory`, and experimental `autoMemory`. Skills are activated with `activate_skill`; subagents still cannot call subagents.
- Gemini extensions can bundle subagents, skills, MCP servers, commands, hooks, and context files. Treat extension packaging as marketplace/plugin work, not the default project-agent path.

## MCP Configuration — per platform

### Copilot CLI / Claude Code (`.mcp.json` at repo root)
```jsonc
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
    }
  }
}
```

### OpenCode (`opencode.json` at repo root)
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_PERSONAL_ACCESS_TOKEN}" },
      "enabled": true
    }
  }
}
```
> OpenCode merges `opencode.json` non-destructively when other config keys exist — preserve them.

### Gemini CLI (`mcp_servers:` in agent frontmatter)
```yaml
---
name: docs-researcher
description: Use when verifying framework APIs through approved docs MCP tools.
kind: local
mcp_servers:
  docs:
    command: node
    args: ["server.js"]
---
```
> Gemini agent-local MCP is isolated to that subagent. Do not write `mcp_servers:` until Phase 3.5 approval has shown the exact YAML block.

## Plan Handoff Placement

Plan prompt output is normalized to HandoffIR before emission; never copy the source prompt frontmatter into runtime agent files.

| Runtime | Handoff placement |
|---|---|
| Copilot CLI | Markdown body section inside `.github/agents/<name>.agent.md`; frontmatter remains Copilot-only. |
| Claude Code | Markdown body section inside `.claude/agents/<name>.md`; frontmatter remains Claude-only. |
| OpenCode | Markdown body section inside `.opencode/agents/<name>.md`; frontmatter remains OpenCode-only and MCP stays in `opencode.json`. |
| OpenAI Codex (CLI + App) | TOML `developer_instructions` in `.codex/agents/<name>.toml`; root `AGENTS.md` keeps only the host delegation trigger, while the full assignment contract lives in `task-delegation`. CLI-only commands stay in usage notes, not required artifact behavior. |
| Gemini CLI | Markdown body section inside `.gemini/agents/<name>.md`; frontmatter remains Gemini-only. Cross-agent handoff says "return to orchestrator" because Gemini subagents cannot call other subagents. |

## Project-Memory Adapters

Root `AGENTS.md` is the single substantive cross-runtime policy file. The
plugin targets 80-120 physical lines and enforces a whole-file maximum of 150
lines and 12,288 UTF-8 bytes after merging. This is plugin policy, not an
OpenAI mandate. Codex's default combined instruction chain is 32 KiB and may be
configured smaller; Claude recommends keeping `CLAUDE.md` under 200 lines.

- Copilot, OpenCode, and Codex consume `AGENTS.md` natively.
- Claude receives a thin `CLAUDE.md` containing `@AGENTS.md` and only approved
  Claude-specific overrides.
- Gemini receives a thin `GEMINI.md` containing `@AGENTS.md` and only approved
  Gemini-specific overrides.
- Prefer these native imports over symlinks or policy copies.

Copilot may combine `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and Copilot
instruction files. Its `@` import expansion applies in `AGENTS.md`,
`CLAUDE.md`, and `.github/copilot-instructions.md`, not `GEMINI.md`. Gemini
expands its own `@` imports. OpenCode treats ordinary Markdown links as
references, not content expansion.

Audit the actual runtime load graph: imports, copies, audience tags, and
multiple native files can add eager context rather than save it. File existence
does not prove a live session loaded an update; record observed load evidence
or require the documented reload/new-session action.

## Generation Loop (pseudocode)

```
for platform in selected_platforms:
    paths   = PATH_MATRIX[platform]
    fmt     = FRONTMATTER[platform]
    if platform == "claude-code":
        write_thin_adapter("CLAUDE.md", import="@AGENTS.md")
    if platform == "gemini-cli":
        write_thin_adapter("GEMINI.md", import="@AGENTS.md")
    for agent in agents:
        write(paths.agents / f"{agent.name}{paths.agent_suffix}",
              render(agent, fmt))
    for skill in skills:
        write(resolve_nonduplicating_skill_path(platform, skill),
              render(skill))
    if approved_mcp_servers:
        merge(paths.mcp_config, approved_mcp_servers, format=fmt.mcp)
verify_runtime_load_graph(selected_platforms)
```

## Anti-patterns

- Writing Copilot frontmatter to a `.claude/agents/*.md` file (Claude will silently ignore unknown keys).
- Using `mcp-servers:` (hyphen) in OpenCode — OpenCode uses top-level `mcp` in `opencode.json`, not per-agent.
- Using a literal OpenCode `permission.question` key — use nested `permission: { question: allow }` or a YAML block.
- Using `mcpServers` or `mcp-servers` in Gemini local subagents — emit `mcp_servers:` and keep the MCP gate.
- Adding Copilot `ask_user` to custom-agent `tools:` — Copilot human input is session-level and subagents return `question_request`.
- Emitting Codex `request_user_input` or `memory` in `.codex/agents/*.toml` — Plan-mode input and native memories are not TOML agent fields.
- Emitting new Codex skills under legacy `.codex/skills/`; use
  `.agents/skills/` and preserve the old tree as migration input.
- Assuming an inherited model is cheap, or emitting `model`/effort fields
  without an explicit pin.
- Treating an import, audience tag, or file's existence as proof that a live
  runtime or delegated child loaded the content.
- Replacing thin `CLAUDE.md` or `GEMINI.md` import adapters with symlinks or
  duplicated policy copies.
- Overwriting `opencode.json` instead of merging the `mcp` key.
- Letting Gemini subagents recursively invoke other subagents — the runtime blocks this, so route fan-out through the parent/orchestrator session.
