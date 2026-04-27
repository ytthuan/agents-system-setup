# Replication — Bidirectional Porting Across Runtimes

This skill can replicate an agent system from one runtime to another (and back) without manual rewrites. The strategy is **Canonical IR (Intermediate Representation) → emit per platform**, not N×N pairwise mappings.

> Supported runtimes: **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**.

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

| IR field | Copilot CLI | Claude Code | OpenCode | OpenAI Codex (CLI + App) |
|---|---|---|---|---|
| `name` | frontmatter `name:` ✅ | frontmatter `name:` ✅ | filename only (no `name:`) ⚠️ derive from basename | TOML `name` in `.codex/agents/<name>.toml` ✅ (orchestrator only as `## <Name>` in `AGENTS.md`; `name` is source of truth) |
| `description` | `description:` ✅ | `description:` ✅ | `description:` ✅ | TOML `description` ✅ |
| `role_prompt` | body ✅ | body ✅ | body ✅ | TOML `developer_instructions` (triple-quoted) ✅ |
| `model.family` | `model: claude-sonnet-4.6` ✅ | `model: sonnet` ✅ | `model: anthropic/claude-sonnet-4-5` ✅ | TOML `model = "gpt-5.4"` ✅ + optional `model_reasoning_effort = "low\|medium\|high"` |
| `tools.*` (bool map) | `tools: [view, grep, ...]` (list) — map names | `tools: Read, Grep, ...` (comma string allowlist) + optional `disallowedTools:` denylist — map names | `permission: { edit, bash, webfetch }` ✅ (legacy `tools: { ... }` map is **deprecated**) | model `sandbox_mode` (`read-only`\|`workspace-write`); fine-grained tool list not enforced — drop with warning ⚠️ |
| `mcp_refs` | per-agent `mcp-servers:` *or* central `.mcp.json` | central `.mcp.json` only ⚠️ | central `opencode.json` › `mcp` only ⚠️ | central `.mcp.json` ✅ **and/or** per-agent `[mcp_servers.<id>]` table inside the agent's TOML ✅ |
| `permission.edit` | n/a — drop with warning ❌ | n/a — drop with warning ❌ | `permission.edit:` ✅ | mapped to `sandbox_mode` (read-only ↔ no edits) ✅ |
| `permission.bash_deny_patterns` | n/a ❌ | n/a ❌ | `permission.bash:` map ✅ | n/a ❌ |
| `scope: user` | `~/.copilot/agents/` | `~/.claude/agents/` | `~/.config/opencode/agents/` | `~/.codex/agents/<name>.toml` |
| `scope: project` | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` | `.codex/agents/<name>.toml` (orchestrator stays in `AGENTS.md`) |
| `nicknames` | n/a — drop ❌ | n/a — drop ❌ | n/a — drop ❌ | TOML `nickname_candidates = ["Atlas", "Delta"]` ✅ (Codex-only IR field; presentation in CLI + App activity views) |
| `security_controls`, `audit_requirements`, `architecture_decisions`, `quality_gates`, `sensitive_paths` | body + `AGENTS.md` managed governance sections ✅ | body + `AGENTS.md` / `CLAUDE.md` memory ✅ | body + `AGENTS.md` / `opencode.json` notes ✅ | TOML `developer_instructions` + `AGENTS.md` managed governance sections ✅ |

### Tool-name canonicalization

| IR canonical | Copilot CLI | Claude Code | OpenCode |
|---|---|---|---|
| `read` | `view` | `Read` | `read` |
| `write` | `create` | `Write` | `write` |
| `edit` | `edit` | `Edit` | `edit` |
| `bash` | `bash` | `Bash` | `bash` |
| `grep` | `grep` | `Grep` | `grep` |
| `glob` | `glob` | `Glob` | `glob` |
| `webfetch` | `web_fetch` | `WebFetch` | `webfetch` |
| `task` | `task` | `Task` | `task` |

The IR uses the lowercase canonical names. Renderers translate **at emit time only** — never round-trip through another platform's name set.

### Codex CLI + App compatibility rule

When Codex is a target, replication emits shared Codex artifacts, not CLI-only behavior: `AGENTS.md` for project/orchestrator memory, `.codex/agents/<name>.toml` for specialized custom agents, and `.codex/config.toml` for `[agents]` defaults. CLI commands such as `/agent`, `/plugins`, and `codex exec` may appear in "Try it" notes, but the replicated TOML must work without relying on those commands as required App behavior.

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
- **Skipping the round-trip verify.** A successful emit isn't success — re-parse and diff IR.
- **Markdown-format replication ledger inside an agents/ directory.** A `.md` file named like `agent-replication.md` placed in `.claude/agents/`, `.codex/agents/`, `.opencode/agents/`, or `.github/agents/` will be parsed as a malformed agent by the runtime and either silently ignored *or* corrupt the agent list. Always write the ledger as `.agents-system-setup/replication.jsonl` (JSON Lines, never `.md`, never inside an agents tree). Same rule applies to any other operational log this skill writes.
- **Dropping governance metadata silently.** Security controls, audit requirements, architecture decisions, quality gates, and sensitive paths must either round-trip or appear in the lossiness report.

## 6. References

- Copilot CLI custom agents: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents
- Claude Code subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- OpenCode agents: https://opencode.ai/docs/agents/
- OpenAI Codex subagents spec (CLI + App activity surfaces): https://developers.openai.com/codex/subagents
- OpenAI Codex (general) AGENTS.md spec: https://agents.md and https://github.com/openai/codex
- Security / audit / architecture baseline: ./security-audit-architecture.md
