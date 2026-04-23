# Replication — Bidirectional Porting Across Runtimes

This skill can replicate an agent system from one runtime to another (and back) without manual rewrites. The strategy is **Canonical IR (Intermediate Representation) → emit per platform**, not N×N pairwise mappings.

> Supported runtimes: **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex CLI**.

## 1. Canonical IR

Every agent, skill, and MCP server is parsed into a single in-memory record. Every emitter renders from this — never from another platform's serialized form.

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

| IR field | Copilot CLI | Claude Code | OpenCode | OpenAI Codex CLI |
|---|---|---|---|---|
| `name` | frontmatter `name:` ✅ | frontmatter `name:` ✅ | filename only (no `name:`) ⚠️ derive from basename | TOML `name` in `.codex/agents/<name>.toml` ✅ (orchestrator only as `## <Name>` in `AGENTS.md`) |
| `description` | `description:` ✅ | `description:` ✅ | `description:` ✅ | TOML `description` ✅ |
| `role_prompt` | body ✅ | body ✅ | body ✅ | TOML `developer_instructions` (triple-quoted) ✅ |
| `model.family` | `model: claude-sonnet-4.6` ✅ | `model: sonnet` ✅ | `model: anthropic/claude-sonnet-4-5` ✅ | TOML `model = "gpt-5.4"` ✅ + optional `model_reasoning_effort = "low\|medium\|high"` |
| `tools.*` (bool map) | `tools: [view, grep, ...]` (list) — map names | `tools: Read, Grep, ...` (comma string allowlist) + optional `disallowedTools:` denylist — map names | `permission: { edit, bash, webfetch }` ✅ (legacy `tools: { ... }` map is **deprecated**) | model `sandbox_mode` (`read-only`\|`workspace-write`); fine-grained tool list not enforced — drop with warning ⚠️ |
| `mcp_refs` | per-agent `mcp-servers:` *or* central `.mcp.json` | central `.mcp.json` only ⚠️ | central `opencode.json` › `mcp` only ⚠️ | central `.mcp.json` ✅ **and/or** per-agent `[mcp_servers.<id>]` table inside the agent's TOML ✅ |
| `permission.edit` | n/a — drop with warning ❌ | n/a — drop with warning ❌ | `permission.edit:` ✅ | mapped to `sandbox_mode` (read-only ↔ no edits) ✅ |
| `permission.bash_deny_patterns` | n/a ❌ | n/a ❌ | `permission.bash:` map ✅ | n/a ❌ |
| `scope: user` | `~/.copilot/agents/` | `~/.claude/agents/` | `~/.config/opencode/agents/` | `~/.codex/agents/<name>.toml` |
| `scope: project` | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` | `.codex/agents/<name>.toml` (orchestrator stays in `AGENTS.md`) |
| `nicknames` | n/a — drop ❌ | n/a — drop ❌ | n/a — drop ❌ | TOML `nickname_candidates = ["Atlas", "Delta"]` ✅ (Codex-only IR field) |

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

## 3. Replication Procedure

Triggered when the user picks **mode: `replicate`** in Phase 1, or when Phase 1 detects two+ runtime footprints and the user confirms a port.

```
1. SOURCE pick:    ask_user "Which runtime is the source of truth?"
2. TARGETS pick:   ask_user "Which runtime(s) should I replicate to?"
                   (multi-select, source excluded)
3. PARSE source files  → AgentIR / SkillIR / MCPServerIR records (in memory)
4. NORMALIZE          → canonical tool names, expand `tools: omitted` to all-true
5. LOSSINESS REPORT   → for each (target × IR field), flag: kept | mapped | dropped
                        Render table; ask_user approval per dropped field.
6. MCP APPROVAL GATE  → re-run Phase 3.5 against any MCPServerIR that will be
                        emitted into a target the user hasn't approved before.
7. EMIT per target    → write per-platform paths + frontmatter (platforms.md)
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
                        equality on (name, description, tools-canonical, mcp_refs).
                        Surface any drift.
```

## 4. Improve Mode (audit + targeted upgrade)

Different from `update` (which re-runs the generator) and `replicate` (which copies across runtimes).

```
1. DETECT current footprint (which runtimes; which artifacts present).
2. AUDIT each artifact against per-platform schema (frontmatter validity,
   description quality, tool minimization, `name`↔filename match, MCP gate
   compliance, Directory Architecture coverage).
3. SCORE: assign each artifact one of {ok, warn, fail} with reasons.
4. PROPOSE deltas as a checklist. For each item show: file, issue, suggested
   fix, blast radius. ask_user multi-select which to apply.
5. APPLY only the approved deltas, with .bak backups (Phase 5 mechanics).
6. SUMMARY: applied / skipped / requires-human counts.
```

Common improve targets:
- Subagent `description` lacks trigger keywords → re-write with concrete verbs.
- `tools:` omitted on a read-only agent → restrict to read+grep+glob.
- MCP server in `.mcp.json` not referenced by any agent → flag for removal.
- `AGENTS.md` missing Directory Architecture or Capability Matrix → regenerate sections inside managed block.
- New marketplace plugin/skill exists for an installed capability (compare against [marketplaces.md](./marketplaces.md)) — surface as opt-in upgrade.

## 5. Anti-patterns

- **Pairwise mappings.** Never write a "copilot→claude" function. Always go through IR.
- **Silent field drops.** A `permission.bash` block with deny patterns must produce a visible warning when emitting Copilot/Claude/Codex (which can't enforce it).
- **Tool-name pass-through.** Writing Claude's `Read` into a Copilot agent (or vice-versa) breaks discovery silently.
- **Replicating without MCP gate.** Replication must re-trigger the MCP approval gate for any new target.
- **Skipping the round-trip verify.** A successful emit isn't success — re-parse and diff IR.
- **Markdown-format replication ledger inside an agents/ directory.** A `.md` file named like `agent-replication.md` placed in `.claude/agents/`, `.codex/agents/`, `.opencode/agents/`, or `.github/agents/` will be parsed as a malformed agent by the runtime and either silently ignored *or* corrupt the agent list. Always write the ledger as `.agents-system-setup/replication.jsonl` (JSON Lines, never `.md`, never inside an agents tree). Same rule applies to any other operational log this skill writes.

## 6. References

- Copilot CLI custom agents: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents
- Claude Code subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- OpenCode agents: https://opencode.ai/docs/agents/
- OpenAI Codex CLI subagents spec: https://developers.openai.com/codex/subagents
- OpenAI Codex (general) AGENTS.md spec: https://agents.md and https://github.com/openai/codex
