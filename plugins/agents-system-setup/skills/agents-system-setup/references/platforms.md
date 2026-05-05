# Multi-Platform Emission Reference

This skill targets five agent runtimes. The user picks one or more in **Phase 0** of the interview; the generator loops over the selection. Runtime drift and supported-surface decisions are tracked in [runtime-updates](./runtime-updates.md).

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
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md`; keep separate from commands; gated by `permission.skill` | not supported natively — describe in `AGENTS.md` | `.gemini/skills/<name>/SKILL.md` (project) or `~/.gemini/skills/<name>/SKILL.md` (user); `.agents/skills/<name>/SKILL.md` also recognized; extension-packaged skills also supported; activation is model-side via skill loading; managed with `/skills`; no `$skill` or `/<skill>` invocation |
| MCP servers | `.mcp.json` (root) | `.mcp.json` (root, shared with Copilot) | `opencode.json` › `"mcp": { ... }` | `.mcp.json` (root, shared) | per-agent `mcp_servers:` in `.gemini/agents/*.md`; extension manifests use `mcpServers`; all MCP writes are approval-gated |
| Hooks | `.github/hooks/*.json` | `.claude/settings.json` › `"hooks"` | `.opencode/hooks/` | not supported | native `settings.json` hooks at project / user / system scope; extension `hooks/hooks.json` when packaging; not extension-only |
| Commands | plugin `commands/<cmd>.md` under plugin root | plugin `commands/<cmd>.md` supported for slash commands (not legacy); project commands at `.claude/commands/<cmd>.md` | `.opencode/commands/<name>.md` or `command` config key; invoked as `/<name>`; `$ARGUMENTS`/`$1` are body placeholders, not invocation syntax; keep separate from skills | not a standard surface | Gemini extensions can bundle `commands/*.md`; no native project command surface |
| Project memory | `AGENTS.md` (root) | `CLAUDE.md` (symlink → `AGENTS.md` on macOS/Linux; copy on Windows) | `AGENTS.md` (native) | `AGENTS.md` (native — primary consumer in Codex CLI + App artifact flows) | `GEMINI.md` is Gemini's native context file; keep it a compact pointer/sync copy of canonical `AGENTS.md` when Gemini is selected |
| Personal memory | `~/.copilot/AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.config/opencode/AGENTS.md` | `~/.codex/AGENTS.md` | `~/.gemini/GEMINI.md` plus `~/.gemini/agents/` |

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
- `vscode` exposes the VS Code chat-host tool set (e.g., `vscode/extensions`, `vscode/runCommands`) when the agent runs inside VS Code Chat. Copilot CLI and other surfaces ignore it harmlessly per the documented "All unrecognized tool names are ignored" rule, so it is safe to ship as a baseline.
- `agent` / `custom-agent` / `Task` enables one custom agent to invoke another. Grant it only to orchestrator-style agents; read-only reviewers should not be able to spawn broad workers.
- `/fleet` is a parent-orchestrated mode for independent subtasks. The generator's wave table should be usable as a `/fleet` prompt, but `/fleet` is optional CLI UX — do not make generated files depend on it.
- If `mcp-servers:` appears in frontmatter, the Phase 3.5 MCP approval gate must have rendered and approved it first, and the rendered agent must carry an `agents-system-setup:mcp-approved` marker.

#### Copilot CLI Standard Tool Profiles

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
name: planner                    # REQUIRED — lowercase + hyphens, unique, matches filename
description: Use when ...        # REQUIRED — drives delegation
tools: Read, Grep, Glob, Bash    # optional comma-string allowlist; omit = inherit all
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
> Project/user/session agents and plugin-shipped agents are not the same schema surface. Project/user/session agents may use richer fields such as `mcpServers`, `hooks`, and `permissionMode`; plugin-shipped agents must not rely on unsupported fields such as `hooks`, `mcpServers`, or `permissionMode`.
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
> Primary agents are selected directly (Tab / configured `switch_agent` keybind). Subagents are invoked automatically by primary agents or manually with `@<agent-name>`. When a subagent creates a child session, users navigate with `session_child_first`, `session_child_cycle`, `session_child_cycle_reverse`, and `session_parent`; include these as "Try it" notes, not schema fields. Gate subagent spawning with `permission.task` when an agent should only call specific workers. Generated orchestrators default to `permission.task` with `"*": deny` plus explicit roster-agent allows.

#### Canonical OpenCode primary task gate

OpenCode primary agents must gate subagent spawning with a `permission.task`
mapping. The wildcard/default entry must be `deny` or `ask`; never emit
`"*": allow`.

```yaml
permission:
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

**Project rules + orchestrator** live in `AGENTS.md` at the repo root (Codex's primary input). `## <Display Name>` headings inside `AGENTS.md` are reserved for **the orchestrator and shared project-wide concerns** (Directory Architecture, Capability Matrix, Waves) — *not* specialized workers.

**Specialized subagents** are standalone TOML files under `.codex/agents/<name>.toml` (project-scoped) or `~/.codex/agents/<name>.toml` (user-scoped). Codex loads each file as a configuration layer for the spawned session, so a custom agent file may override any setting a normal session config sets. In the CLI, switch threads with `/agent`; in the App, rely on Codex's surfaced subagent activity rather than embedding CLI-only switching requirements.

**Required fields** (per [openai docs](https://developers.openai.com/codex/subagents)):

| Field                    | Type     | Purpose                                                         |
| ------------------------ | -------- | --------------------------------------------------------------- |
| `name`                   | string   | Source of truth for the agent identity (filename is convention only). |
| `description`            | string   | Human-facing guidance for when Codex should use this agent.     |
| `developer_instructions` | string   | Core instructions defining behavior (use TOML triple-quoted string). |

**Optional fields** (inherit from parent session if omitted): `nickname_candidates: string[]`, `model`, `model_reasoning_effort` (`low`|`medium`|`high`), `sandbox_mode` (e.g. `read-only`, `workspace-write`), `[mcp_servers.<id>]` table, `[[skills.config]]` array. Built-in agent names — `default`, `worker`, `explorer` — can be overridden by a custom file using the same `name`. `nickname_candidates` are display hints that can help in both Codex CLI and App activity views.

```toml
name = "reviewer"
description = "Use when reviewing PRs for correctness, security, and missing tests."
model = "gpt-5.4"
model_reasoning_effort = "high"
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
max_threads = 6                  # default 6
max_depth = 1                    # default 1; raise only if you truly need recursive delegation
job_max_runtime_seconds = 1800   # optional global job timeout
```

Codex reads `.mcp.json` at repo root (shared with Copilot/Claude). Per-agent MCP servers may also be declared inline via `[mcp_servers.<id>]` in the agent's TOML.

For high-volume row-per-agent fan-out, Codex exposes `spawn_agents_on_csv`; document it as an advanced workflow rather than a default orchestrator requirement. Codex plugin manifests may also point to `skills`, `mcpServers`, `apps`, interface assets, `.app.json`, and `.mcp.json`; keep those component references in plugin docs and never auto-write MCP/app config without the approval gate.

Codex source-backed runtime notes:
- Current Codex releases enable subagent workflows by default, but Codex only spawns subagents when explicitly asked. The orchestrator may say "spawn one agent per row/concern" and Codex handles child threads, waits for results, and returns a consolidated response.
- Subagents inherit the current sandbox policy and live runtime approval overrides. A custom TOML `sandbox_mode` can narrow defaults, but interactive `/approvals` or `--yolo` choices still apply to spawned child sessions.
- `agents.max_threads` caps concurrent open child threads; `agents.max_depth = 1` is the safe default to avoid recursive fan-out; `agents.job_max_runtime_seconds` supplies the default timeout for CSV jobs.
- `spawn_agents_on_csv` requires an input CSV, an instruction template, and exactly one `report_agent_job_result` call per worker. Exported CSV status and metadata are an advanced batch workflow, not the default multi-agent topology.
- Plugin marketplace files can live at `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, or user-level `~/.agents/plugins/marketplace.json`; plugin roots keep `.codex-plugin/plugin.json` plus optional `skills/`, `.mcp.json`, `.app.json`, and `assets/`.

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
- The docs prose shows `mcpServers`, but the loader schema validates `mcp_servers`. Emit snake_case `mcp_servers:` and normalize imported camelCase examples with a warning.
- Remote A2A subagents (`kind: remote`, `agent_card_url`, `agent_card_json`, `auth`) are advanced/import-only; do not emit them by default.
- Gemini CLI supports native skills loaded from `.gemini/skills/<name>/SKILL.md` (project) or `~/.gemini/skills/<name>/SKILL.md` (user); `.agents/skills/<name>/SKILL.md` is also recognized. Activation is model-side via skill loading; use `/skills` to manage loaded skills. There is no `$skill` or `/<skill>` invocation syntax — skills are not slash commands.
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
| OpenAI Codex (CLI + App) | TOML `developer_instructions` in `.codex/agents/<name>.toml`; `AGENTS.md` keeps only orchestrator/project-level handoff summary. CLI-only commands stay in usage notes, not required artifact behavior. |
| Gemini CLI | Markdown body section inside `.gemini/agents/<name>.md`; frontmatter remains Gemini-only. Cross-agent handoff says "return to orchestrator" because Gemini subagents cannot call other subagents. |

## Project-Memory Linking

If both Copilot/OpenCode (use `AGENTS.md`) and Claude Code (uses `CLAUDE.md`) are selected:

- **macOS/Linux**: `ln -s AGENTS.md CLAUDE.md`
- **Windows**: copy `AGENTS.md` → `CLAUDE.md` and prepend `<!-- generated from AGENTS.md — re-copy on every update -->`. Re-copy on each `update` run.

If Gemini CLI is selected, keep `GEMINI.md` as a compact pointer or sync copy of canonical `AGENTS.md` because Gemini's native context file is `GEMINI.md`. Use the same OS-specific symlink/copy caution as Claude Code.

Detect platform with `uname -s` (Darwin/Linux ⇒ symlink; otherwise copy).

## Generation Loop (pseudocode)

```
for platform in selected_platforms:
    paths   = PATH_MATRIX[platform]
    fmt     = FRONTMATTER[platform]
    if platform == "gemini-cli":
        write("GEMINI.md", render("assets/GEMINI.md.template"))
    for agent in agents:
        write(paths.agents / f"{agent.name}{paths.agent_suffix}",
              render(agent, fmt))
    for skill in skills:
        write(paths.skills / skill.name / "SKILL.md", render(skill))
    if approved_mcp_servers:
        merge(paths.mcp_config, approved_mcp_servers, format=fmt.mcp)
link_project_memory(selected_platforms)
```

## Anti-patterns

- Writing Copilot frontmatter to a `.claude/agents/*.md` file (Claude will silently ignore unknown keys).
- Using `mcp-servers:` (hyphen) in OpenCode — OpenCode uses top-level `mcp` in `opencode.json`, not per-agent.
- Using `mcpServers` or `mcp-servers` in Gemini local subagents — emit `mcp_servers:` and keep the MCP gate.
- Symlinking `CLAUDE.md` or `GEMINI.md` on Windows.
- Overwriting `opencode.json` instead of merging the `mcp` key.
- Letting Gemini subagents recursively invoke other subagents — the runtime blocks this, so route fan-out through the parent/orchestrator session.
