# Replication — Bidirectional Porting Across Runtimes

This skill can replicate an agent system from one runtime to another (and back) without manual rewrites. The strategy is **Canonical IR (Intermediate Representation) → emit per platform**, not N×N pairwise mappings.

> Supported runtimes: **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**, and **Gemini CLI**.
>
> Runtime drift and advanced/import-only surfaces are tracked in [runtime-updates](./runtime-updates.md).

## 1. Canonical IR

Every agent, skill, and MCP server is parsed into a single in-memory record. Every emitter renders from this — never from another platform's serialized form.

For generated output, apply [context optimization](./context-optimization.md): preserve IR fidelity, but render compact governance summaries inline and link overflow details when the selected profile is `Balanced` or `Compact`.

### 1a. AgentIR
```yaml
name: <kebab-case>                    # MUST equal filename basename
description: "Use when ..."           # discovery surface — required
role_prompt: |                        # full markdown body after frontmatter
  ...
model:
  family: sonnet | haiku | opus | gpt-5 | inherit | unspecified
  vendor: anthropic | openai | google | unspecified
source_scope: managed | session | project | user | plugin | extension | unknown
agent_invocation:
  explicit: "@agent | /agent | cli-flag | task-tool | none"
  automatic: true|false
limits:
  max_turns: <integer|null>
  timeout_seconds: <integer|null>
  job_max_runtime_seconds: <integer|null>
  timeout_mins: <integer|null>           # Gemini local subagent timeout
tools:
  read:    true|false
  write:   true|false
  edit:    true|false
  bash:    true|false
  grep:    true|false
  glob:    true|false
  webfetch:true|false
  task:    true|false                 # subagent-spawn capability
mcp_refs: [<server-name>, ...]        # references to MCPServerIR.name
plugin_component_refs:                # optional plugin-bundled components
  skills: [<skill-name>, ...]
  apps: [<app-id>, ...]
  hooks: [<hook-id>, ...]
  lsp: [<server-name>, ...]
permission:                           # OpenCode-style; degrades on others
  edit: allow | ask | deny
  bash_deny_patterns: ["git push", ...]
scope: project | user | session
owns_paths: ["src/auth/**", ...]      # from AGENTS.md Directory Architecture
trigger_keywords: [auth, login, ...]  # parsed from description
security_controls:                   # governance baseline; see security-audit-architecture.md
  - { control: "secrets handling", source: "GitHub Code Security", evidence: "secret scan" }
audit_requirements:
  - "return build/test/security evidence before done"
architecture_decisions:
  - { decision: "API boundary", pattern: "ports-and-adapters", adr: "ADR-0001" }
quality_gates:
  - { gate: "tests", evidence: "npm test", required: true }
sensitive_paths: [".env*", ".mcp.json", ".github/workflows/**"]
surface_lossiness:
  - "CLI-only slash command unavailable in app/web UI"
gemini:
  display_name: <string|null>
  temperature: <number|null>
  kind: local | remote | unspecified
```

### 1b. SkillIR
```yaml
name: <kebab-case>
description: "Use when ..."
argument_hint: "<...>"
body: |                               # full markdown body
  ...
assets:                               # optional bundled files
  - { path: "scripts/foo.sh", role: script }
  - { path: "templates/x.md", role: template }
```

### 1c. MCPServerIR
```yaml
name: github
transport: stdio | http | sse
command: ["npx", "-y", "@modelcontextprotocol/server-github"]
url: null                             # only for http/sse
env:
  GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"
enabled: true
```

## 2. Field-Mapping Matrix (lossless / lossy markers)

| IR field | Copilot CLI | Claude Code | OpenCode | OpenAI Codex (CLI + App) | Gemini CLI |
|---|---|---|---|---|---|
| `name` | frontmatter `name:` ✅ | frontmatter `name:` ✅ | filename only (no `name:`) ⚠️ derive from basename | TOML `name` in `.codex/agents/<name>.toml` ✅ (orchestrator only as `## <Name>` in `AGENTS.md`; `name` is source of truth) | frontmatter `name:` ✅; filename should match basename |
| `description` | `description:` ✅ | `description:` ✅ | `description:` ✅ | TOML `description` ✅ | `description:` ✅; drives automatic delegation |
| `role_prompt` | body ✅ | body ✅ | body ✅ | TOML `developer_instructions` (triple-quoted) ✅ | Markdown body system prompt ✅ |
| `model.family` | `model: claude-sonnet-4.6` ✅ | `model: sonnet` ✅ | `model: anthropic/claude-sonnet-4-5` ✅ | TOML `model = "gpt-5.4"` ✅ + optional `model_reasoning_effort = "low\|medium\|high"` | `model: gemini-...` ✅ plus `temperature:` |

> Replication preserves explicit `model:` overrides only. When the source agent left `model:` blank, emit `model: inherit` (or omit it where the target runtime treats absence as inherit). Never invent ids — see [models](./models.md) for accepted formats per target.

> **Task Assignment preservation:** replication preserves the full Task Assignment Contract structure ([handoff.md](./handoff.md#delegation-packet-canonical-schema)). Required-minimum fields are 1:1 across runtimes; expansion blocks (Goal & Definition of Done, Scope, File Inventory, Verification Protocol, Reporting Protocol, etc.) must be carried into the target agent body. Codex TOML keeps the structure inside `developer_instructions`; never silently drop expansion blocks during replication. Surface any drop in the lossiness report.
| `tools.*` (bool map) | `tools: [read, search, edit, execute, agent]` aliases ✅ | `tools: Read, Grep, ...` (comma string allowlist) + optional `disallowedTools:` denylist — map names | `permission: { edit, bash, webfetch }` ✅ (legacy `tools: { ... }` map is **deprecated**) | model `sandbox_mode` (`read-only`\|`workspace-write`); fine-grained tool list not enforced — drop with warning ⚠️ | `tools:` allowlist ✅; map only known Gemini tool names and warn on unknown/discovered-only tools |
| `mcp_refs` | per-agent `mcp-servers:` *or* central `.mcp.json` | central `.mcp.json` only ⚠️ | central `opencode.json` › `mcp` only ⚠️ | central `.mcp.json` ✅ **and/or** per-agent `[mcp_servers.<id>]` table inside the agent's TOML ✅ | per-agent `mcp_servers:` ✅; extension `mcpServers` import/package surface ⚠️ |
| `permission.edit` | n/a — drop with warning ❌ | n/a — drop with warning ❌ | `permission.edit:` ✅ | mapped to `sandbox_mode` (read-only ↔ no edits) ✅ | map to narrower `tools:` and/or policy-engine guidance ⚠️ |
| `permission.bash_deny_patterns` | n/a ❌ | n/a ❌ | `permission.bash:` map ✅ | n/a ❌ | policy-engine `subagent` rules can enforce command prefixes ⚠️ |
| `source_scope` | project/user paths ✅ | managed/session/project/user/plugin precedence ✅ | project/user paths + JSON config ✅ | project/user TOML paths ✅ | project/user paths ✅; extension-bundled agents are package/import surface |
| `agent_invocation` | `/agent`, `--agent`, prompt mention, `/fleet`, and Task/orchestrator guidance ✅ | subagent `Agent`-tool guidance + session `--agents` note; agent teams are separate opt-in primitive ✅ | Task/orchestrator + `@` autocomplete + child-session notes ✅ | CLI `/agent` note only; App activity is display-driven ⚠️ | automatic delegation by description + explicit `@<agent>` ✅; no recursive subagent calls ⚠️ |
| `limits.max_turns` | n/a — drop with warning ❌ | `maxTurns` ✅ | `steps` maps partially ⚠️ | n/a — drop with warning ❌ | `max_turns` ✅ |
| `limits.timeout_seconds` | n/a ❌ | n/a ❌ | n/a ❌ | `[agents].job_max_runtime_seconds` for global job timeout ⚠️ | `timeout_mins` (rounded up to minutes) ⚠️ |
| `plugin_component_refs` | plugin skills/hooks/MCP/LSP refs ✅ | plugin skills/hooks refs, but plugin-shipped agents cannot rely on `hooks`, `mcpServers`, or `permissionMode` ⚠️ | OpenCode hooks/MCP refs via config ⚠️ | `.codex-plugin/plugin.json` `skills`, `mcpServers`, `apps`, assets ✅ | Gemini extension refs for MCP, commands, context, hooks, skills, subagents ⚠️ |
| `surface_lossiness` | body/output contract ✅ | body/output contract ✅ | body/output contract ✅ | required for CLI-only vs App-visible behavior ✅ | required for non-recursive delegation, remote A2A import-only, and docs/schema `mcpServers`→`mcp_servers` normalization ✅ |
| `scope: user` | `~/.copilot/agents/` | `~/.claude/agents/` | `~/.config/opencode/agents/` | `~/.codex/agents/<name>.toml` | `~/.gemini/agents/<name>.md` |
| `scope: project` | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` | `.codex/agents/<name>.toml` (orchestrator stays in `AGENTS.md`) | `.gemini/agents/<name>.md` |
| `nicknames` | n/a — drop ❌ | n/a — drop ❌ | n/a — drop ❌ | TOML `nickname_candidates = ["Atlas", "Delta"]` ✅ (Codex-only IR field; presentation in CLI + App activity views) | map one display value to `display_name` ⚠️ |
| `security_controls`, `audit_requirements`, `architecture_decisions`, `quality_gates`, `sensitive_paths` | body + `AGENTS.md` managed governance sections ✅ | body + `AGENTS.md` / `CLAUDE.md` memory ✅ | body + `AGENTS.md` / `opencode.json` notes ✅ | TOML `developer_instructions` + `AGENTS.md` managed governance sections ✅ | body + `GEMINI.md`/`AGENTS.md` governance summary ✅ |

### Tool-name canonicalization

| IR canonical | Copilot CLI | Claude Code | OpenCode | Gemini CLI |
|---|---|---|---|---|
| `read` | `read` (compatible: `view`, `Read`) | `Read` | `read` | `read_file` |
| `write` | `edit` (compatible: `Write`) | `Write` | `write` | runtime-discovered write tool; warn if unknown |
| `edit` | `edit` | `Edit` | `edit` | runtime-discovered edit tool; warn if unknown |
| `bash` | `execute` (compatible: `shell`, `Bash`, `powershell`) | `Bash` | `bash` | `run_shell_command` |
| `grep` | `search` (compatible: `Grep`) | `Grep` | `grep` | `grep_search` |
| `glob` | `search` (compatible: `Glob`) | `Glob` | `glob` | runtime-discovered glob/search tool; warn if unknown |
| `webfetch` | `web` | `WebFetch` | `webfetch` | runtime-discovered web tool or MCP tool; warn if unknown |
| `task` | `agent` (compatible: `custom-agent`, `Task`) | `Agent` | `task` | n/a inside subagents; root can use `@<agent>` / subagent tools |

The IR uses the lowercase canonical names. Renderers translate **at emit time only** — never round-trip through another platform's name set.

### Codex CLI + App compatibility rule

When Codex is a target, replication emits shared Codex artifacts, not CLI-only behavior: `AGENTS.md` for project/orchestrator memory, `.codex/agents/<name>.toml` for specialized custom agents, and `.codex/config.toml` for `[agents]` defaults. CLI commands such as `/agent`, `/plugins`, and `codex exec` may appear in "Try it" notes, but the replicated TOML must work without relying on those commands as required App behavior.

### Gemini CLI support rule

Gemini CLI is a supported local-subagent target. Replication emits `.gemini/agents/<name>.md` with `kind: local`, loader-valid `mcp_servers:`, and Markdown body prompts. It must report lossiness for recursive delegation (Gemini subagents cannot call subagents), remote A2A fields (`kind: remote`, `agent_card_url`, `agent_card_json`, `auth`; import/advanced only), and any tool names that cannot be mapped to Gemini's runtime-discovered tool registry.

## 3. Replication Procedure

Triggered when the user picks **mode: `replicate`** in Phase 1, or when Phase 1 detects two+ runtime footprints and the user confirms a port.

```
1. SOURCE pick:    ask_user "Which runtime is the source of truth?"
2. TARGETS pick:   ask_user "Which runtime(s) should I replicate to?"
                   (multi-select, source excluded)
3. PARSE source files  → AgentIR / SkillIR / MCPServerIR records (in memory)
4. NORMALIZE          → canonical tool names, expand `tools: omitted` to all-true
5. LOSSINESS REPORT   → for each (target × IR field), flag: kept | mapped | dropped
                         Render a compact table; ask_user approval per dropped field.
                         Link overflow details if the table exceeds the chosen profile.
                        Also flag surface lossiness, such as source CLI-only usage
                        instructions that must not become required Codex App behavior.
6. MCP APPROVAL GATE  → re-run Phase 3.5 against any MCPServerIR that will be
                        emitted into a target the user hasn't approved before.
7. EMIT per target    → write per-platform paths + frontmatter/TOML (platforms.md)
                        with `<!-- agents-system-setup:replicated-from: <source> -->`
                        marker just under the frontmatter.
8. WRITE ledger       → append one JSON object per line to
                        `.agents-system-setup/replication.jsonl` at the repo root.
                        **NEVER** place the ledger inside any agents/ directory
                        (`.claude/agents/`, `.codex/agents/`, `.opencode/agents/`,
                        `.github/agents/`) and **NEVER** use a `.md` extension —
                        agent loaders walk those trees by extension and will
                        treat the file as a malformed agent.
                        Each line:
                        `{"ts":"<ISO8601>","source":"<runtime>","targets":["..."],
                         "files":[{"path":"...","sha256":"..."}]}`
9. VERIFY round-trip  → re-parse the emitted files back to IR; assert structural
                        equality on (name, description, tools-canonical, mcp_refs,
                        governance metadata that the target can represent).
                        Surface any drift.
```

## 4. Improve Mode (audit + targeted upgrade)

Different from `update` (which re-runs the generator) and `replicate` (which copies across runtimes).

```
1. DETECT current footprint (which runtimes; which artifacts present).
2. AUDIT each artifact against per-platform schema (frontmatter validity,
   description quality, tool minimization, `name`↔filename match, MCP gate
   compliance, Directory Architecture coverage) and the governance baseline:
   Security & Audit Matrix, Threat Model, Architecture / Design Pattern Matrix,
   ADR plan, Quality Gates, least-privilege tool boundaries, secrets handling,
   dependency/supply-chain provenance, and source-backed recommendations.
3. SCORE: assign each artifact and governance category one of
   {ok, warn, fail, requires-human} with reasons.
4. PROPOSE deltas as a checklist. For each item show: file, issue, suggested
   fix, blast radius, source reference, and evidence required. ask_user
   multi-select which to apply.
5. APPLY only the approved deltas, with .bak backups (Phase 5 mechanics).
6. SUMMARY: applied / skipped / requires-human counts.
```

Common improve targets:
- Subagent `description` lacks trigger keywords → re-write with concrete verbs.
- `tools:` omitted on a read-only agent → restrict to read+grep+glob.
- MCP server in `.mcp.json` not referenced by any agent → flag for removal.
- `AGENTS.md` missing Directory Architecture or Capability Matrix → regenerate sections inside managed block.
- `AGENTS.md` missing Context Loading Policy, Security & Audit Matrix, Threat Model, Architecture / Design Pattern Matrix, ADR Index, or Quality Gates → regenerate sections inside managed block.
- Agent can write secrets/MCP/CI/release/dependency paths without a security owner → downgrade tools or require orchestrator/security review.
- Plugin/MCP/skill recommendation has no source URL or untrusted source → remove or replace with a tiered marketplace candidate.
- Design-pattern guidance is absent or contradictory → add architecture reviewer delta and ADR plan.
- New marketplace plugin/skill exists for an installed capability (compare against [marketplaces.md](./marketplaces.md)) — surface as opt-in upgrade.

## 5. Anti-patterns

- **Pairwise mappings.** Never write a "copilot→claude" function. Always go through IR.
- **Silent field drops.** A `permission.bash` block with deny patterns must produce a visible warning when emitting Copilot/Claude/Codex (which can't enforce it).
- **Tool-name pass-through.** Writing Claude's `Read` into a Copilot agent (or vice-versa) breaks discovery silently.
- **Replicating without MCP gate.** Replication must re-trigger the MCP approval gate for any new target.
- **Writing Gemini docs spelling blindly.** `mcpServers` appears in upstream prose, but generated local Gemini agents must use loader-valid `mcp_servers:`.
- **Recursive Gemini workers.** Gemini subagents cannot invoke other subagents; root/orchestrator must own fan-out.
- **Skipping the round-trip verify.** A successful emit isn't success — re-parse and diff IR.
- **Markdown-format replication ledger inside an agents/ directory.** A `.md` file named like `agent-replication.md` placed in `.claude/agents/`, `.codex/agents/`, `.opencode/agents/`, or `.github/agents/` will be parsed as a malformed agent by the runtime and either silently ignored *or* corrupt the agent list. Always write the ledger as `.agents-system-setup/replication.jsonl` (JSON Lines, never `.md`, never inside an agents tree). Same rule applies to any other operational log this skill writes.
- **Dropping governance metadata silently.** Security controls, audit requirements, architecture decisions, quality gates, and sensitive paths must either round-trip or appear in the lossiness report.

## 6. References

- Copilot CLI custom agents: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents
- Claude Code subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- OpenCode agents: https://opencode.ai/docs/agents/
- OpenAI Codex subagents spec (CLI + App activity surfaces): https://developers.openai.com/codex/subagents
- OpenAI Codex (general) AGENTS.md spec: https://agents.md and https://github.com/openai/codex
- Runtime update audit and support tracking: ./runtime-updates.md
- Gemini CLI subagents: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md
- Gemini CLI agent loader schema: https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/agents/agentLoader.ts
- Gemini CLI extensions: https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md
- Security / audit / architecture baseline: ./security-audit-architecture.md
