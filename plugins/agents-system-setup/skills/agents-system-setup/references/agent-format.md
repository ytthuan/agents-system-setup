# Custom Agent Format — per platform

This skill targets five runtimes. **Use the right schema for each** — agents written in Copilot frontmatter will be silently ignored by Claude Code, and vice versa. Runtime drift and support decisions are tracked in [runtime-updates](./runtime-updates.md).

For path matrix and full examples, see [platforms.md](./platforms.md).

## Copilot CLI (`.github/agents/<name>.agent.md`)

Source: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents#agent-profile-format
How-to: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli

Emitter rule: keep writing `.github/agents/<name>.agent.md`. GitHub concept docs also mention `.github/agents/<name>.md`; recognize that path during audit/import as an upstream drift signal, but do not switch generation until CLI behavior is confirmed.

```markdown
---
name: <kebab-case-name>           # MUST match filename basename
description: 'Use when ... <trigger keywords>.'
model: claude-sonnet-4.6          # OPTIONAL
tools:                            # OPTIONAL whitelist; omit = inherit all
  - vscode                        # public alias for the VS Code chat-host tool set (safe baseline)
  - execute                       # public alias for shell tools
  - read                          # public alias for file read/view
  - edit
  - search                        # public alias for grep/glob
  - agent                         # only for orchestrator-style agents
  - todo                          # public alias for TodoWrite
mcp-servers:                      # OPTIONAL — hyphenated key
  github:
    command: npx
    args: ['-y', '@modelcontextprotocol/server-github']
    env: { GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN} }
---

# <Display Name>
(prompt body)
```

> Use Copilot's documented tool aliases for new output: `vscode`, `execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`. Product-specific aliases (`Bash`, `Read`, `Grep`, `Glob`, `Task`) are accepted by Copilot as compatible aliases, but emitting the public aliases keeps profiles portable. `/fleet` can use these custom agents for parallel subtasks; it is an optional CLI workflow, not a file schema.
>
> Apply the [Copilot CLI Standard Tool Profiles](./platforms.md#copilot-cli-standard-tool-profiles) at emit time: `standard` (`[vscode, execute, read, agent, edit, search, todo]`) for orchestrators and edit-capable subagents, `read-only` (`[read, search]`) for reviewers/auditors, `runner` for testers/release helpers, `research` for documentation gatherers, or `inherit` to omit `tools:` entirely. The role → profile mapping is the source of truth for Phase 4 generation.
>
> Human input is a session tool (`ask_user`) and is disabled by `--no-ask-user`. Do **not** add `ask_user` to custom-agent `tools:` profiles because it is not a documented custom-agent tool alias. Copilot subagents return `question_request` to the orchestrator/session.

## Claude Code (`.claude/agents/<name>.md`)

Source: https://docs.claude.com/en/docs/claude-code/sub-agents

Only `name` and `description` are required. The body becomes the system prompt. Subagents start in the main conversation's CWD; `cd` does not persist between Bash calls (use `isolation: worktree` for an isolated repo copy).

```markdown
---
name: <kebab-case-name>           # REQUIRED — lowercase letters and hyphens; unique
description: Use when ... <triggers>.   # REQUIRED — when Claude should delegate
tools: Read, Grep, Glob, Bash, AskUserQuestion # OPTIONAL comma-separated allowlist; omit = inherit all
disallowedTools: Write, Edit      # OPTIONAL — denylist; applied before `tools`
model: sonnet                     # OPTIONAL — sonnet | opus | haiku | <full-id> | inherit (default)
permissionMode: default           # OPTIONAL — default | acceptEdits | auto | dontAsk | bypassPermissions | plan
maxTurns: 20                      # OPTIONAL — agentic-turn cap
skills: [code-review, lint]       # OPTIONAL — full skill content injected at startup (NOT inherited from parent)
mcpServers:                       # OPTIONAL — name reference OR inline server config
  slack: {}
hooks: { ... }                    # OPTIONAL — lifecycle hooks scoped to this subagent
memory: project                   # OPTIONAL — user | project | local (cross-session memory)
background: false                 # OPTIONAL — run as background task
effort: medium                    # OPTIONAL — low | medium | high | xhigh | max (model-dependent)
isolation: worktree               # OPTIONAL — isolated git worktree copy of repo
color: blue                       # OPTIONAL — red|blue|green|yellow|purple|orange|pink|cyan
initialPrompt: "Begin by ..."     # OPTIONAL — auto-submitted first turn when run as main agent
---

You are a <role>...
(prompt body — this is the system prompt)
```

> Tool names are Claude's canonical names: `Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `Agent`, `WebFetch`. Do **not** use Copilot's tool names here. If both `tools` and `disallowedTools` are set, `disallowedTools` is applied first, then `tools` is resolved against the remaining pool.
>
> **Scopes & precedence** (highest→lowest): managed settings → `--agents` CLI JSON → `.claude/agents/` (project) → `~/.claude/agents/` (user) → plugin `agents/`. Higher-priority same-name subagents override lower ones. Project subagents are discovered by walking up from CWD; `--add-dir` paths are NOT scanned.
>
> **Schema split:** project/user/session subagents can use the richer field set above. Plugin-shipped agents are narrower: do not rely on `hooks`, `mcpServers`, or `permissionMode` in plugin-bundled agent files.
> Plugin-shipped agents do support `memory`; keep that separate from unsupported hook/MCP/permission fields.
>
> Add `AskUserQuestion` to restrictive `tools:` allowlists only when the agent is expected to ask the user. Otherwise subagents report `question_request` to the orchestrator.
>
> **Primitive split:** a Claude subagent file is a reusable definition. Tool-based subagent invocation via `Agent` launches that definition inside the current session and returns a summary to the caller. Agent teams are a separate experimental feature: independent Claude Code instances, peer-to-peer messages, and a shared task list; only use them when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled and the work benefits from teammate discussion.

## OpenCode (`.opencode/agents/<name>.md` or `~/.config/opencode/agents/<name>.md`)

Source: https://opencode.ai/docs/agents/

Only `description` is required. **The markdown filename becomes the agent name** (`review.md` → `review`). Built-in primaries: `build`, `plan`. Built-in subagents: `general`, `explore`. The `tools:` field is **deprecated** — prefer `permission:` for new configs.

```markdown
---
description: Use when ...           # REQUIRED
mode: subagent                      # OPTIONAL — primary | subagent | all (default: all)
model: anthropic/claude-sonnet-4-20250514   # OPTIONAL — provider/model-id format
temperature: 0.1                    # OPTIONAL — 0.0-1.0 (defaults are model-specific)
top_p: 0.9                          # OPTIONAL — alternative to temperature
prompt: "{file:./prompts/review.txt}"   # OPTIONAL — external system-prompt file (relative to config)
steps: 5                            # OPTIONAL — max agentic iterations
disable: false                      # OPTIONAL — set true to disable
hidden: false                       # OPTIONAL — hide from @ autocomplete (still callable via Task)
color: accent                       # OPTIONAL — hex (#FF5733) or theme (primary|secondary|accent|success|warning|error|info)
permission:                         # OPTIONAL — preferred over deprecated `tools:`
  question: allow                    # OPTIONAL — official human-input tool
  edit: deny                        # allow | ask | deny
  webfetch: deny
  bash:
    "*": ask                        # put wildcard FIRST, specific rules after (last match wins)
    "git status *": allow
    "git push": deny
  task:                             # OPTIONAL — gate which subagents this agent may invoke
    "*": deny
    "code-reviewer": allow
# Any other top-level keys (e.g. reasoningEffort, textVerbosity) are passed through
# directly as provider model options — provider-specific.
---

You are a <role>...
```

> **MCP** is NOT configured in agent frontmatter — declare servers globally in `opencode.json` › `mcp`. Per-agent allow/deny is via `permission:`. The `tools:` map (e.g. `{ write: false }`) still works but is deprecated; prefer `permission:` for `edit`/`bash`/`webfetch` and `permission.task` for subagent gating.
>
> Markdown agents remain the default emitter. `opencode.json` can also define agents under top-level `agent`; treat JSON agent config as an import/update target only when the user explicitly asks for JSON emission.
>
> Permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `todowrite`, `webfetch`, `websearch`, `codesearch`, `lsp`, `skill`, `question`, `doom_loop`.
>
> Human input uses the `question` tool. Grant it with nested YAML (`permission: { question: allow }` or the block above), not a literal dotted key. OpenCode does not provide durable auto-learning beyond AGENTS.md, skills, compaction, and plugin patterns.
>
> `mode: primary` agents are directly selectable; `mode: subagent` agents are invoked by primary agents or manually with `@<agent-name>`. Use `permission.task` to constrain which subagents a primary or broad worker may spawn. Child sessions are navigated with OpenCode's `session_child_first`, `session_child_cycle`, `session_child_cycle_reverse`, and `session_parent` keybinds; keep those in usage notes, not frontmatter.

## OpenAI Codex CLI + App — split layout: `AGENTS.md` + `.codex/agents/*.toml`

Source: https://developers.openai.com/codex/subagents · general AGENTS.md spec: https://agents.md

Codex uses **two complementary shared artifact surfaces** that should stay compatible with both Codex CLI and Codex App wherever the App has access to the repo artifacts:

1. **`AGENTS.md`** at the repo root — project memory + orchestrator instructions + Directory Architecture / Capability Matrix / Waves. The orchestrator MAY appear here as `## Orchestrator`.
2. **`.codex/agents/<name>.toml`** (project) or **`~/.codex/agents/<name>.toml`** (user) — one TOML file per specialized subagent. Codex loads each as a session config layer; the CLI can switch threads with `/agent`.

Keep **CLI-only** commands and workflows (`codex plugin marketplace add`, `/plugins`, `/agent`, `codex exec`, local approval overlays) in install or "Try it" notes. Do not make generated artifacts depend on those commands for Codex App behavior.

```toml
name = "reviewer"
description = "Use when reviewing PRs for correctness, security, and missing tests."
model = "gpt-5.4"                       # optional; inherits from session if omitted
model_reasoning_effort = "high"         # optional: low|medium|high
sandbox_mode = "read-only"              # optional: read-only|workspace-write
nickname_candidates = ["Atlas", "Delta"]  # optional, presentation only
developer_instructions = """
You are a senior reviewer. Lead with concrete findings.
Prioritize correctness, security, behavior regressions, and missing tests.
"""

[mcp_servers.openaiDeveloperDocs]       # optional, per-agent MCP allowlist
url = "https://developers.openai.com/mcp"

[[skills.config]]                        # optional, per-agent skill toggle
path = "/abs/path/to/SKILL.md"
enabled = false
```

### Codex TOML summary + pointer rule

`developer_instructions` cannot link inline, so every Codex subagent risks duplicating long security/architecture/output prose. Apply the **summary + pointer** rule regardless of output profile:

1. Lead with a 2-3 line role/outcome statement.
2. Reference the canonical Delegation Packet from [`handoff.md`](./handoff.md#delegation-packet-canonical-schema) and tell Codex to fill it from its session.
3. Point to specific `AGENTS.md` rows by name ("AGENTS.md › Security & Audit Matrix › row `<owner>`") rather than re-stating them in TOML.
4. Keep an explicit short checklist only when the agent owns sensitive surfaces (MCP, secrets, CI/release, dependency manifests, generated scripts).
5. Keep the `Outcome first` and `Handoff status` lines because Codex sessions surface those directly.

Validators warn when a Codex subagent's `developer_instructions` block grows beyond ~60 lines because it usually means the pointer rule was skipped.

Codex shared artifact rules:
- **Required fields**: `name`, `description`, `developer_instructions`. Missing any → silent skip.
- **`name` is the source of truth and generated files keep it equal to the filename stem**. Imported custom files may differ, but replication should report that as drift; built-ins (`default`, `worker`, `explorer`) may still be overridden by reusing the name.
- **Global config** in `.codex/config.toml`: `[agents] max_threads = 6`, `max_depth = 1`, and optional `job_max_runtime_seconds` defaults.
- Human input: `request_user_input` is Plan-mode only. It is not a TOML field; Codex child/default/exec flows return `question_request`.
- Native memories: `[features] memories = true` and `~/.codex/memories/` exist but are off by default and may be region-limited. Do not emit `memory` in agent TOML.
- MCP servers can be shared via `.mcp.json` at repo root *or* declared per-agent inside the TOML.
- Read-only identity rule: Codex agents whose `name` or filename stem identifies
  them as reviewer, auditor, security, architect, or governance roles set
  `sandbox_mode = "read-only"`. Agents with empty Owned paths should also be
  read-only at generation time; validators can enforce identity surfaces, but
  cannot infer Owned paths from TOML alone.
- Skills: per-agent enable/disable via `[[skills.config]]` array entries.
- `nickname_candidates` are display hints for Codex CLI and App activity views; they are not routing keys.
- Advanced fan-out: `spawn_agents_on_csv` can launch a row-per-agent workflow. Document it as an explicit workflow, not a default generated behavior; every worker must report exactly once with `report_agent_job_result`.
- Codex plugin manifests can reference `skills`, `mcpServers`, `apps`, interface assets, `.app.json`, and `.mcp.json`. Marketplace files may be repo-scoped under `.agents/plugins/marketplace.json` or compatible Claude-style roots. Keep app/MCP writes approval-gated.

## Gemini CLI (`.gemini/agents/<name>.md` or `~/.gemini/agents/<name>.md`)

Sources:
- Subagents: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md
- Loader schema: https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/agents/agentLoader.ts
- Extensions: https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md

Gemini CLI local subagents are Markdown files with YAML frontmatter. The body is the subagent's system prompt. The parent Gemini agent sees each subagent as a tool and may delegate automatically by description or explicitly when the user starts a prompt with `@<agent-name>`.

Emitter rule: write **local** subagents by default. Remote A2A subagents are import/advanced only and require explicit user approval because they add auth and remote trust boundaries.

```markdown
---
name: reviewer
description: Use when reviewing code for correctness and security.
kind: local
display_name: Reviewer
tools:
  - read_file
  - grep_search
  - run_shell_command
  - ask_user
mcp_servers: {}
model: gemini-3-flash-preview
temperature: 0.1
max_turns: 20
timeout_mins: 10
---

You are a reviewer...
```

Gemini local-subagent rules:
- Required fields: `name`, `description`. Use `kind: local` explicitly for generated files.
- Optional fields: `display_name`, `tools`, `mcp_servers`, `model`, `temperature`, `max_turns`, `timeout_mins`.
- Names are slug-like (`[a-z0-9-_]+`) and should match the filename basename.
- `tools:` is an allowlist. Omit it to inherit parent tools; use wildcards (`*`, `mcp_*`, `mcp_<server>_*`) only with rationale.
- Human input uses `ask_user`; include it only for interactive agents expected to ask. Headless or restricted agents return `question_request`.
- Native memory includes `save_memory`, `GEMINI.md`, `/memory`, and experimental `autoMemory`. Gemini skills use `activate_skill`.
- Emit snake_case `mcp_servers:`. Upstream prose examples may show `mcpServers`, but the loader schema validates `mcp_servers`; normalize imported camelCase with a warning.
- Subagents cannot invoke other subagents, even with wildcard tools; in validator wording, **subagents must not recursively call subagents**. Cross-agent work returns to the orchestrator/root session.
- Files whose basename starts with `_` are ignored by Gemini's agent loader.
- Remote A2A import fields are `kind: remote`, `agent_card_url`, `agent_card_json`, and `auth`; do not emit them for local project agents unless explicitly requested and approved.

## Human Input Surface

Use [human-input](./human-input.md) for the canonical matrix and
`question_request` schema.

| Runtime | Valid emitted syntax | Pitfall |
|---|---|---|
| Copilot CLI | Session/orchestrator calls `ask_user`; subagents return `question_request`. | Do not add `ask_user` to custom-agent `tools:`. |
| Claude Code | `tools: Read, AskUserQuestion` when a restrictive allowlist must permit questions. | Plugin agents support `memory`, but not `hooks`, `mcpServers`, or `permissionMode`. |
| OpenCode | `permission: { question: allow }` or a nested YAML block. | Do not write a literal `permission.question` key. |
| OpenAI Codex CLI + App | `request_user_input` in Plan mode; `question_request` elsewhere. | Do not emit human-input or memory fields in `.codex/agents/*.toml`. |
| Gemini CLI | `tools: [ask_user]` for interactive ask-capable agents. | Subagents cannot call subagents; headless flows return `question_request`. |

## Discovery Surface (all platforms)

The router/orchestrator picks a subagent based on the **`description`** field (or `description` in `.codex/agents/<name>.toml` for Codex).

- Always start with `"Use when ..."`
- Include concrete trigger keywords from the user's domain
- Quote any description containing colons

## Plan Handoff Surface

The VS Code `plan` prompt (`agent: Plan`) and Spec-Kit `/plan` output are planning inputs, not agent file formats. Normalize them to HandoffIR (see [handoff](./handoff.md)), then place the handoff in the target runtime's supported surface:

- Copilot CLI / Claude Code / OpenCode / Gemini CLI: Markdown body section after valid runtime-specific YAML frontmatter.
- OpenAI Codex (CLI + App): `developer_instructions` inside `.codex/agents/<name>.toml`, plus project-level summary in `AGENTS.md`. CLI-only interaction notes must stay optional.

## Common Pitfalls

- `name` mismatch with filename → silent ignore (Copilot, Claude).
- Unquoted colon in `description` → YAML parse failure → silent ignore.
- Missing `description` → never auto-invoked.
- Using Copilot's `tools:` *list* in a Claude file (Claude expects a comma-separated *string*).
- Using Claude's `model: sonnet` in an OpenCode file (OpenCode expects `provider/model`).
- Embedding `mcp-servers:` in an OpenCode agent (use `opencode.json` instead).
- Writing OpenCode `permission.question: allow` as a literal key instead of nested `permission`.
- Adding `ask_user` to Copilot custom-agent tools.
- Emitting Codex `request_user_input` or `memory` in agent TOML.
- Embedding `mcpServers` in a Gemini local subagent (emit `mcp_servers:`).
- Asking a Gemini subagent to call another subagent (the runtime prevents recursive subagent calls).
- Overlapping responsibilities between two subagents → orchestrator picks wrong one. Make boundaries explicit in `## Out of scope` and in the **Directory Architecture** in `AGENTS.md`.

## Tool Restriction Patterns (use the platform's syntax)

| Pattern | Copilot CLI | Claude Code | OpenCode | OpenAI Codex (CLI + App) | Gemini CLI |
|---|---|---|---|---|---|
| Read-only reviewer | `tools: [read, search]` | `tools: Read, Grep, Glob` | `permission: { edit: deny, bash: deny, webfetch: deny }` | `sandbox_mode = "read-only"` in `.codex/agents/<name>.toml` | `tools: [read_file, grep_search]`; no subagent recursion |
| Implementer (full) | omit `tools:` or include `edit`/`execute` aliases | omit `tools:` | omit `permission:` or set scoped `ask` rules | `sandbox_mode = "workspace-write"` (or omit to inherit) | omit `tools:` to inherit, or explicitly allow edit/shell tools available in the user's Gemini tool registry |
| Docs writer | `tools: [read, edit, search]` | `tools: Read, Edit, Write` | `permission: { edit: allow, bash: deny, webfetch: ask }` | `sandbox_mode = "workspace-write"`; describe scope in `developer_instructions` | `tools: [read_file, grep_search]` plus write tools only when docs paths are owned |

## MCP Per-Agent Reference

- **Copilot CLI** — list servers under `mcp-servers:` in agent frontmatter, or define centrally in `.mcp.json`.
- **Claude Code** — central `.mcp.json` (shared with Copilot when both target the repo).
- **OpenCode** — central `opencode.json` `mcp` key only; agents reference by name via the runtime's discovery.
- **OpenAI Codex (CLI + App)** — central `.mcp.json` plus optional per-agent `[mcp_servers.<id>]` in TOML where supported; keep approval-gated and surface any App support uncertainty as lossiness.
- **Gemini CLI** — per-agent `mcp_servers:` in `.gemini/agents/*.md` for local subagents; extension manifests use `mcpServers`. Emit only after Phase 3.5 approval.

## Optional placeholder substitution table

Renderers must replace these placeholders before writing generated runtime
agent directories. Literal `{{OPTIONAL_...}}` placeholders are allowed only in
this repository's templates under `assets/`.

Content-quality placeholders such as `{{CONTENT_QUALITY_STATUS}}`,
`{{CONTENT_QUALITY_CURATOR}}`, `{{CONTENT_QUALITY_OWNER}}`,
`{{CONTENT_QUALITY_SIGNALS}}`, and `{{CONTENT_QUALITY_REFERENCE}}` are normal
managed-content placeholders in `AGENTS.md` and related templates. They are not
runtime frontmatter fields. For Codex TOML, keep content-quality guidance inside
`developer_instructions`; do not emit unsupported fields such as
`content_quality`, `ask_user`, `question`, `request_user_input`, or `memory`.

General default: when a feature is off, unsupported, or not applicable, replace
the placeholder with an empty string and remove the surrounding blank line or
empty YAML/TOML key. When a feature is on, render the runtime-native line or
block exactly at the placeholder indentation. Never leave a literal optional
placeholder in generated runtime agent directories.

| Placeholder | On form | Off / not-applicable form |
|---|---|---|
| `{{OPTIONAL_MODEL_LINE}}` | Runtime-native model line, for example `model: <id>` in YAML frontmatter. | Empty string. |
| `{{OPTIONAL_TOOLS_BLOCK}}` | Runtime-native tools allowlist, for example Copilot YAML list, Claude comma string, or Gemini YAML list. | Empty string to inherit/default tools. |
| `{{OPTIONAL_MCP_SERVERS_BLOCK}}` | Approved runtime-native MCP block: Copilot `mcp-servers:`, Claude `mcpServers:`, or Gemini `mcp_servers:`. | Empty string and no MCP key. |
| `{{OPTIONAL_MCP_APPROVAL_MARKER}}` | Markdown body marker `<!-- agents-system-setup:mcp-approved: <approval-ref> -->`. | Skipped marker `<!-- agents-system-setup:mcp-skipped: no MCP written -->` when MCP was considered; otherwise empty string. |
| `{{OPTIONAL_MCP_APPROVAL_COMMENT}}` | Top-level Codex TOML comment body `agents-system-setup:mcp-approved: <approval-ref>` rendered as `# agents-system-setup:mcp-approved: <approval-ref>`. | `agents-system-setup:mcp-skipped: no MCP written` when skipped, or `agents-system-setup:mcp-not-applicable` when no MCP was considered. |
| `{{OPTIONAL_PERMISSION_TASK_BLOCK}}` | OpenCode primary-agent `permission.task` block with `"*": deny` first and approved roster entries set to `allow`, or `"*": ask` only after explicit approval. | Empty string for non-OpenCode/non-primary agents; for OpenCode primary agents with no delegated subagents, render `"*": deny`. |
| `{{OPTIONAL_DISPLAY_NAME_LINE}}` | Gemini `display_name: <human-readable name>`. | Empty string. |
| `{{OPTIONAL_TEMPERATURE_LINE}}` | Runtime-native `temperature: <number>` line. | Empty string. |
| `{{OPTIONAL_MAX_TURNS_LINE}}` | Runtime-native max-turn line: Claude `maxTurns: <int>` or Gemini `max_turns: <int>`. | Empty string. |
| `{{OPTIONAL_TIMEOUT_MINS_LINE}}` | Gemini `timeout_mins: <int>`. | Empty string. |
| `{{OPTIONAL_STEPS_LINE}}` | OpenCode `steps: <int>`. | Empty string. |
| `{{OPTIONAL_HIDDEN_LINE}}` | OpenCode `hidden: true` or `hidden: false` when the plan explicitly sets visibility. | Empty string to use OpenCode's default. |
| `{{OPTIONAL_PERMISSION_BLOCK}}` | OpenCode subagent `permission:` block with least-privilege `deny`/`ask` defaults and any approved scoped `allow` rules. | Empty string to inherit default permissions only when the plan permits it. |
| `{{OPTIONAL_DISALLOWED_TOOLS_BLOCK}}` | Claude `disallowedTools: <comma-separated tool list>`. | Empty string. |
| `{{OPTIONAL_PERMISSION_MODE_LINE}}` | Claude `permissionMode: <mode>` when explicitly selected. | Empty string. |
| `{{OPTIONAL_EFFORT_LINE}}` | Claude `effort: <effort>` when explicitly selected (`low`, `medium`, `high`, `xhigh`, or `max`). | Empty string. |
| `{{OPTIONAL_ISOLATION_LINE}}` | Claude `isolation: worktree` when the plan requests isolated worktrees. | Empty string. |
| `{{OPTIONAL_SKILLS_BLOCK}}` | Claude `skills: [...]` block when skills are explicitly attached to that subagent. | Empty string. |

### MCP approval placeholders

`{{OPTIONAL_MCP_APPROVAL_MARKER}}` is Markdown-safe and belongs in the agent
body, not frontmatter. `{{OPTIONAL_MCP_APPROVAL_COMMENT}}` is Codex TOML-safe:
the template prefixes it with `#`, so the renderer substitutes the comment body
without a leading `#`.

For Codex TOML, place the resulting approval comment as a **top-level TOML
comment** before any `[mcp_servers.<id>]`, `[[mcp_servers]]`, or
`[[mcp_servers.<id>]]` table. Do not put approval evidence inside
`developer_instructions` or inside an MCP table.

### `{{OPTIONAL_PERMISSION_TASK_BLOCK}}` (OpenCode primary YAML frontmatter)

Default approved roster gate:

```yaml
permission:
  question: allow
  task:
    "*": deny
    "<subagent-name>": allow
```

MCP skipped or no delegated subagents:

```yaml
permission:
  question: allow
  task:
    "*": deny
```

Human-approved broad delegation must stay non-permissive by default:

```yaml
permission:
  question: allow
  task:
    "*": ask
```

Never emit `permission.task` with `"*": allow`.

**Any change to MCP requires the Phase 3.5 approval gate.**
