---
name: agents-system-setup
description: 'Bootstrap, update, improve, or replicate a multi-agent system across GitHub Copilot CLI, Claude Code, OpenCode, and OpenAI Codex CLI. Generates AGENTS.md (Directory Architecture, Agent Roster, Capability Matrix, Security & Audit Matrix, Threat Model, Architecture/Design Decisions), an orchestrator + N subagents, project-scoped skills, and opt-in plugin/MCP recommendations sourced from vendor-official catalogs. Detects existing systems on entry; bidirectional replication via a single Canonical IR (no pairwise rewrites). Cross-OS (Linux/macOS/Windows). Mandatory MCP approval gate, security/audit baseline, and architecture/design-pattern rationale. Recommends GitHub Spec-Kit for software-dev domains. USE FOR: "set up agents", "scaffold AGENTS.md", "init agents system", "improve my agents", "audit agent setup", "architecture review", "security audit agents", "port agents from copilot to claude code", "replicate agents", "configure copilot/claude/opencode/codex for this repo", "discover plugins/MCP servers". DO NOT USE FOR: editing a single existing agent file, unrelated coding work, MCP server implementation.'
argument-hint: '[init | update | improve | replicate] (omit to auto-detect)'
---

# Setup Copilot Agents (multi-platform)

Scaffold or update a complete agent system for the current project across **Copilot CLI**, **Claude Code**, **OpenCode**, and/or **OpenAI Codex CLI**. Produces a canonical `AGENTS.md` (with **Directory Architecture**, **Agent Roster**, **Capability Matrix**, **Security & Audit Matrix**, **Threat Model**, and **Architecture / Design Decisions**), an **orchestrator + N subagents**, project-scoped **skills**, and **approved** plugins/MCP servers — derived from a structured interview.

## When to Use

- Brand-new repository needs an agent setup from scratch (**init**)
- Existing project should adopt or extend the orchestrator + subagent pattern (**update**)
- Existing agent system needs an audit and targeted upgrades (**improve**)
- Agents authored for one runtime need to be ported to another (**replicate** — Copilot ↔ Claude Code ↔ OpenCode ↔ Codex CLI)
- Discovering relevant plugins / MCP servers from the well-known marketplaces

## Hard Rules

1. **Always interview first** with `ask_user`. Never assume project type, language, scope, or target platform.
2. **Detect existing agent footprint on entry.** If any of `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `~/.codex/AGENTS.md` exists, present mode choice with `improve` and `replicate` as first-class options — never silently jump to `update`.
3. **Orchestrator + subagent topology is mandatory.** Subagent count (3 to ~50) is decided dynamically from scope.
4. **Directory Architecture is generated and enforced.** Every subagent file references it; the orchestrator routes by ownership.
5. **Per-item opt-in recommendations.** Plugin / skill / MCP candidates are always presented with rationale and explicit `ask_user` choice — never bulk-applied silently.
6. **MCP config approval gate.** Before writing any MCP config (`.mcp.json`, `opencode.json` › `mcp`, agent `mcp-servers:`), render the proposal and call `ask_user` for approval. No silent MCP writes — ever. Replication re-triggers this gate per new target.
7. **Marketplace-first lookup with vendor attribution.** Recommendations come from registries listed in [marketplaces](./references/marketplaces.md), tagged `[Tier · Vendor]` — never invent names or URLs.
8. **Replication goes through Canonical IR, not pairwise mappings.** See [replication](./references/replication.md). Never write a Copilot→Claude (or any other direction) function; always parse → IR → emit.
9. **Non-destructive updates.** `cp <file> <file>.bak` before any edit; merge into managed blocks, preserve user-authored content.
10. **Multi-platform aware.** Emit per-platform paths and frontmatter per [platforms](./references/platforms.md). Never write Copilot frontmatter into a Claude file.
11. **Cross-OS aware.** Detect host OS once (Linux / macOS / Windows-bash / Windows-pwsh) per [cross-platform](./references/cross-platform.md). Pick `.sh` for POSIX shells, `.ps1` for native PowerShell. Forward slashes in generated docs. Never symlink on Windows. Bundle `.gitattributes` so line endings stay correct on every clone.
12. **Git is optional and gated by `ask_user`.**
13. **Parallelism is mandatory where work is independent.** The generator computes parallel-safety from the Directory Architecture and emits a wave table; the orchestrator prompt always contains a fan-out clause. For Claude Code, also emit `AGENT-TEAMS.md` per [parallelism](./references/parallelism.md). Sequential-only topologies are an error.
14. **If the project domain is software-development, recommend GitHub Spec-Kit.** After domain detection (Phase 1.7), if the brief matches a software-dev keyword set, present spec-kit as an opt-in companion via `ask_user`, never auto-install. See [spec-kit](./references/spec-kit.md).
15. **Security, audit, architecture, and design-pattern governance are mandatory.** Every plan and generated `AGENTS.md` must include the baseline from [security-audit-architecture](./references/security-audit-architecture.md): Security & Audit Matrix, Threat Model, Architecture / Design Pattern Matrix, ADR plan, and Quality Gates. Small projects may merge roles, but not omit the concerns.
16. **Security-sensitive writes require evidence.** MCP config, secrets-adjacent paths, CI/release config, and generated scripts must have an owner, approval state, and verification evidence in the output contract. No broad write permissions without rationale.
17. **Improve mode is evidence-based.** Existing systems are scored for security boundaries, secrets, audit evidence, architecture ownership, design-pattern consistency, and supply-chain source trust before any delta is applied.

## Procedure

### Phase 0 — Platform Selection

First question after detecting cwd. Use `ask_user`:

> "Which agent runtime(s) should I configure?"
> Choices: `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex CLI only", "Copilot CLI + Claude Code", "All four (Copilot + Claude Code + OpenCode + Codex)"]`

Persist the selection. All later phases loop over selected platforms using [platforms.md](./references/platforms.md) as the source of truth for paths and frontmatter.

### Phase 1 — Detect & Choose Mode

1. **Inspect cwd** and detect runtime footprint:
   - Project files: `package.json`, `*.csproj`, `Package.swift`, `build.gradle`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `mkdocs.yml`, `.git/`.
   - Agent artifacts (per runtime):
     - Copilot CLI: `AGENTS.md`, `.github/agents/`, `.github/skills/`, `.mcp.json`
     - Claude Code: `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/settings.json`
     - OpenCode: `opencode.json`, `.opencode/agents/`, `.opencode/skills/`
     - Codex CLI: `AGENTS.md` (orchestrator + project rules), `.codex/agents/*.toml` (specialized subagents), `.codex/config.toml`, `~/.codex/AGENTS.md`, `~/.codex/agents/`
2. **Decide mode** with `ask_user` — show what was detected:

   | Detected footprint | Default offer | Choices |
   |---|---|---|
   | Nothing | `init` | `["Init (Recommended)", "Cancel"]` |
   | One runtime, looks healthy | `improve` | `["Improve current setup (Recommended)", "Update (regenerate managed blocks)", "Replicate to another runtime", "Init alongside (additive)"]` |
   | One runtime, gaps | `update` | `["Update (Recommended)", "Improve (audit + targeted fixes)", "Replicate to another runtime"]` |
   | Two+ runtimes | `improve` | `["Improve current setup (Recommended)", "Replicate / sync between runtimes", "Update one runtime"]` |

3. Run the interview — see [interview script](./references/interview.md). One question per `ask_user` call. Skip questions already answered by detection (project type, framework). For `improve`/`replicate`, jump straight to Phase 1.5.

### Phase 1.5 — Improve / Replicate branch

If the user picked **improve** → run the [improve procedure](./references/replication.md#4-improve-mode-audit--targeted-upgrade) (audit → score → propose deltas → opt-in apply). Skip Phases 2–4; jump to Phase 5 mechanics for backups + write.

If the user picked **replicate** → run the [replication procedure](./references/replication.md#3-replication-procedure):
1. `ask_user` for **source** runtime (single-select among detected).
2. `ask_user` for **target** runtimes (multi-select; source excluded).
3. Parse source → AgentIR / SkillIR / MCPServerIR records.
4. Render lossiness report; `ask_user` to approve dropped fields per target.
5. Re-run **Phase 3.5** MCP approval gate against each new target.
6. Emit per target with `<!-- agents-system-setup:replicated-from: <source> -->` markers.
7. Write replication ledger to `.agents-system-setup/replication.jsonl` (one JSON object per line — **never `.md`, never inside any `agents/` directory**, or it will be misread as a malformed agent).
8. Verify round-trip (re-parse emitted → diff IR → surface drift).

For both branches, finish with Phase 7 (verify & summarize).

### Phase 1.7 — Domain Detection & Spec-Kit Recommendation

Run after Phase 1 (and 1.5 if branched), before Phase 2. Inspect the project brief gathered during interview against this software-development keyword set:

`app, application, api, service, microservice, library, sdk, cli, tool, devtool,
backend, frontend, fullstack, web, mobile, ios, android, desktop,
framework, plugin, extension, package, module,
infrastructure, infra, terraform, pulumi, kubernetes, helm,
compiler, parser, runtime, database, orm`.

If **any** keyword matches (case-insensitive, word-boundary), or the project already has source-language signals (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `*.csproj`, `pom.xml`, `Package.swift`, `build.gradle`, `mix.exs`, `composer.json`), classify as `software-dev`. Otherwise `non-dev` (marketing, research, content, data-analysis).

If `software-dev`, call `ask_user`:

> "This looks like a software project. Would you like to install **GitHub Spec-Kit** (Spec-Driven Development: `/specify` → `/plan` → `/tasks` → `/implement` slash commands) alongside the agent system?"
> Choices: `["Yes — install for this runtime (Recommended)", "Just print the install command", "No, skip"]`

On approval, emit the runtime-matched command from [spec-kit](./references/spec-kit.md) (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` then `specify init --here --ai <copilot|claude|codex|opencode>`). Print, never silently shell-out unless the user picked "install".

Record the choice in the plan so Phase 4 orchestrator output can reference the `/specify` workflow when appropriate.

### Phase 1.8 — Security, Audit, Architecture Intake

Run after domain detection and before Phase 2. Use [security-audit-architecture](./references/security-audit-architecture.md) as the source of truth.

Ask only questions not already answered by detection:

1. Data sensitivity.
2. Auth boundary.
3. External tools / MCP usage.
4. Audit evidence expectations.
5. Deployment / release risk.
6. Architecture style.
7. Critical quality attributes.
8. Known design anti-patterns to avoid.

Record the answers in the plan. If the user is unsure, choose safe defaults: least privilege, no silent MCP writes, no secrets in code, architecture decisions documented in `AGENTS.md`, and dedicated security/architecture ownership when the project handles sensitive data or external tools.

### Phase 2 — Plan (Directory Architecture, Roster, Matrix, Waves)

Build the plan and show it before writing anything. The plan must include:

- **Directory Architecture** — table of `path glob | purpose | owner agent | edit rule`. Derived from project type + frameworks. Always covers: source dirs, tests, docs, infra, agent files, generated artifacts.
- **Agent Roster** — table of `name | role | owns | triggers | model (optional) | parallel-safe | wave`. Use [topology guide](./references/topology.md). Compute parallel-safety per [parallelism](./references/parallelism.md): a subagent is parallel-safe iff its `owns` glob doesn't overlap any other's, it doesn't write outside `owns`, and it doesn't depend on another subagent's output in the same wave.
- **Capability Matrix** — capabilities × agents grid (✅ / 🟡).
- **Wave plan** — grouped list `Wave N → [parallel-safe subagents]`; the orchestrator fans out per wave and awaits each before the next.
- Skills to create.
- Plugin/MCP candidates **per capability** (Phase 3 fills this).
- Per-platform file plan (Copilot/Claude/OpenCode/Codex paths the user will actually get).
- Git actions (if any).
- **Security & Audit Matrix** — controls, owner agents, affected paths, evidence required, and source reference.
- **Threat Model Summary** — assets, trust boundaries, threats, mitigations, owners, and status.
- **Architecture & Design Pattern Matrix** — selected patterns, alternatives, rationale, risks/guardrails, and ADR refs.
- **ADR plan** — decisions that should become docs if the user approves docs writes.
- **Quality Gates** — build/test/lint/security/supply-chain/architecture evidence required before "done".

End the phase with `ask_user`: `["Proceed", "Edit plan first"]`.

### Phase 3 — Marketplace Lookup with per-item Opt-in

For every capability the user named (e.g., "playwright", "azure", "postgres"):

1. **Search** the marketplaces in tier order — see [marketplaces](./references/marketplaces.md). Tier 1 first; only fall through if it misses.
2. Collect **at most 3 candidates per capability**. For each, populate **mandatory rationale fields**: `name`, `source_tier`, `repo_url`, `bundles` (agents/skills/hooks/MCP/LSP), `why_recommended`, `tradeoffs`, `install_command_per_platform`. Empty rationale ⇒ drop the candidate.
3. Render a **comparison table** to the user, then call `ask_user`:
   > "For capability **<x>**, which would you like?"
   > Choices: `["<candidate 1 — short label>", "<candidate 2>", "<candidate 3>", "Show more (Tier-3 fallback search)", "None — skip this capability"]`
4. **Show more** triggers Tier-3 search (capped at +5 additional candidates). Re-render table and re-prompt.
5. Record the user's pick. Skipped capabilities never reach the MCP gate or final write.

See [plugin discovery](./references/plugin-discovery.md) for the comparison-table format and rationale schema.

### Phase 3.5 — MCP Config Approval Gate (mandatory, downstream of Phase 3)

If any user-selected candidate from Phase 3 includes an MCP server:

1. Build the proposed config **per platform**:
   - Copilot CLI / Claude Code → `.mcp.json` (`mcpServers` key)
   - OpenCode → merge into `opencode.json` (`mcp` key)
2. Render each proposed file verbatim (full JSON).
3. `ask_user`:
   > "I'm about to write the MCP configuration above to `<paths>`. Approve?"
   > Choices: `["Approve all (Recommended)", "Approve selectively (per-server)", "Skip MCP entirely"]`
4. If **selective**, loop per server: `["Include", "Skip"]`.
5. If **skip**, strip every `mcp-servers:` from generated agents and do not write `.mcp.json` / `opencode.json` `mcp` key.
6. **No MCP write may occur before this gate returns approval.**

### Phase 4 — Generate Artifacts (per platform, post-approval)

For each selected platform, look up paths and frontmatter in [platforms.md](./references/platforms.md), then render:

- `AGENTS.md` at repo root → [template](./assets/AGENTS.md.template). Fill **Directory Architecture**, **Agent Roster**, **Capability Matrix**, **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, **Quality Gates**, **Skills**, **Plugins/MCP** tables.
- Orchestrator → [template](./assets/orchestrator.agent.md.template) at the platform's agents path.
- Each subagent → [template](./assets/subagent.agent.md.template) at the platform's agents path. Fill `{{OWNED_PATHS}}` / `{{READONLY_PATHS}}` from the Directory Architecture.
  - **Codex CLI exception:** subagents are NOT rendered as `## <Name>` headings in `AGENTS.md`. Instead, emit one `.codex/agents/<kebab-name>.toml` per subagent with required fields `name`, `description`, `developer_instructions` (use TOML triple-quoted basic string). Carry the IR's `tool_allowlist` only if explicitly set (otherwise inherit from parent session). Map IR `model` → `model` and `model` reasoning hints → `model_reasoning_effort` (`low`|`medium`|`high`). Set `sandbox_mode = "read-only"` for read-only subagents. Per-agent MCP servers go under `[mcp_servers.<id>]` in the same file. `AGENTS.md` keeps only the orchestrator section + Directory Architecture / Capability Matrix / Waves. See [Codex layout](./references/platforms.md#openai-codex-cli--split-layout) and [openai docs](https://developers.openai.com/codex/subagents). Also emit/upsert `.codex/config.toml` with `[agents] max_threads = 6` and `max_depth = 1` unless the user supplied other values.
- Each skill → [template](./assets/skill.template.md) at the platform's skills path.
- MCP config (only if Phase 3.5 approved) at the platform's MCP path.
- Drop the [directory-architecture snippet](./assets/directory-architecture.snippet.md) into any agent missing the boundary block.
- **Orchestrator parallelism clause** — render the wave-aware fan-out instructions per [parallelism](./references/parallelism.md). The orchestrator must invoke all parallel-safe subagents of a wave in a single response (multiple Task-tool calls), await all results, then start the next wave.
- **Governance baseline** — render the security, audit, architecture, design-pattern, ADR, and quality-gate sections from Phase 1.8 / Phase 2. Subagents that touch sensitive paths, MCP/tool config, CI/release config, dependency manifests, or architecture boundaries must include explicit security boundaries and audit evidence expectations.
- **Spec-Kit block** — if Phase 1.7 recorded `spec_kit_installed = true`, render `assets/spec-kit-block.snippet.md` into the `{{SPEC_KIT_BLOCK}}` placeholder of `AGENTS.md` (substituting `{{RUNTIME}}` per platform: `copilot|claude|codex|opencode`). If `false`, replace the placeholder with an empty string. See [spec-kit](./references/spec-kit.md).
- **Claude Code AGENT-TEAMS.md** — when Claude Code is among the selected platforms AND the Agent Roster has 3+ subagents marked `team-suitable` (independent + benefits from peer challenge), emit `AGENT-TEAMS.md` documenting: opt-in env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), settings.json snippet, suggested teammate roster, token-cost warning, and when to fall back to parallel subagents.

**Project-memory linking** (after AGENTS.md is written):
- If both Claude Code and another platform are selected → pick by detected OS (see [cross-platform](./references/cross-platform.md)):
  - **macOS / Linux / WSL**: `bash ./scripts/link-project-memory.sh` → symlinks `CLAUDE.md → AGENTS.md`.
  - **Windows native**: `pwsh -File ./scripts/link-project-memory.ps1` → tries symlink (Developer Mode/admin), falls back to copy with regenerable header (re-runs keep them in sync).
- OpenCode reads `AGENTS.md` natively — no linking required.

**Frontmatter rules** (silent-failure traps):
- `name` MUST match filename basename (kebab-case).
- Quote any `description` containing colons.
- Subagent `description` MUST start with `"Use when..."`.
- Use the **right frontmatter schema per platform** (see [platforms.md](./references/platforms.md) — Copilot uses `mcp-servers:`, Claude uses comma-string `tools:`, OpenCode uses `mode:` and bool-keyed `tools:` map).
- Restrict tools per subagent to the minimum needed.
- The `model:` line is optional in every platform — emit only if the user specified an override.

### Phase 5 — Update Mode (non-destructive)

For every existing target file:
1. `cp <file> <file>.bak` via bash before any edit.
2. Parse existing frontmatter; preserve user-authored sections.
3. Merge new content under `<!-- agents-system-setup:managed:start -->` … `<!-- agents-system-setup:managed:end -->` markers — replace the block, never duplicate.
4. Print a diff summary at the end.

### Phase 6 — Optional Git Init

Only if user confirmed in Phase 1 AND no `.git/` exists. Pick the script that matches the host OS — see [cross-platform](./references/cross-platform.md):

```bash
# macOS / Linux / Git Bash / WSL
bash ./scripts/git-init.sh
```

```powershell
# Windows native PowerShell (PowerShell 7+ recommended)
pwsh -File ./scripts/git-init.ps1
# or, on stock Windows PowerShell 5.1:
powershell.exe -ExecutionPolicy Bypass -File ./scripts/git-init.ps1
```

Both forms initialize `main`, write a stack-aware `.gitignore` (covering `.github/`, `.claude/`, `.opencode/` local state, `.DS_Store`, `Thumbs.db`, `desktop.ini`), drop a `.gitattributes` for line endings, stage, and commit.

### Phase 7 — Verify & Summarize

1. List every file created/modified with absolute paths, grouped by platform.
2. Re-read each generated agent/skill: confirm `name` matches filename, `description` present, no unquoted colons, frontmatter parses for the *target platform's* schema.
3. Verify `AGENTS.md` contains non-empty **Directory Architecture**, **Agent Roster**, **Capability Matrix**.
4. Verify `AGENTS.md` contains non-empty **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, and **Quality Gates**. If a concern is not applicable, it must still have an explicit `n/a` rationale.
5. Verify security-sensitive files (`.mcp.json`, `opencode.json`, `.env*`, CI/release config, lockfiles, generated scripts) have an owner and evidence requirement in the governance sections.
6. Print "Try it" examples per selected platform (`copilot`, `claude`, `opencode`).
7. Suggest 2–3 next customizations.

### Phase 8 — Final Wrap-Up (single consolidated ask)

Run after Phase 7, **before** exiting. One multi-select question presents a curated, source-cited menu of well-known add-ons (Spec-Kit, evals, OpenTelemetry GenAI, OWASP LLM Top-10, Claude Code hooks, prompt versioning, cost budgets, additional subagent catalogs). Filtered by signals from Phase 1.7 (domain), Phase 3 (plugins), Phase 3.5 (MCP), and selected target platforms — never show items already installed. Each selected item dispatches to a dedicated skill if available, else runs the inline action documented in [wrap-up](./references/wrapup.md).

1. Build the candidate list per the filter matrix in [wrap-up](./references/wrapup.md#filter-matrix).
2. Present a **single** multi-select via the runtime's ask-user tool (never per-item round-robin).
3. For each selection: re-confirm only if the action edits config outside `AGENTS.md`; then execute.
4. Append `✅ Wrap-up add-ons selected/skipped` lines to the Output Contract.

Skip the entire phase only when `mode == update` and no agents/plugins/MCP changed.

## Decision Aids

- **How many subagents?** [topology guide](./references/topology.md). One subagent per durable concern — also a path owner in the Directory Architecture.
- **Skill vs Subagent?** Reusable workflow with assets → Skill. Context isolation / different tool restrictions → Subagent.
- **Plugin vs MCP?** Plugins extend the runtime; MCP servers expose tools to agents. External-system integrations are usually MCP.
- **Dedicated security/architecture agent or merged role?** Dedicated when the repo handles sensitive data, external tools/MCP, CI/release, regulated domains, monorepos, or user-requested architecture work. Merge into `@reviewer` only for small projects, and keep explicit ownership in the Security & Audit Matrix.
- **Which platform?** Copilot CLI for GitHub-tight teams; Claude Code for Anthropic-first; OpenCode for vendor-neutral / self-hosted; Codex CLI for OpenAI-first (uses split layout: `AGENTS.md` for orchestrator + rules, `.codex/agents/*.toml` for specialized subagents). Multi-target if uncertain — files coexist cleanly via shared `AGENTS.md` + `.mcp.json`.
- **`update` vs `improve` vs `replicate`?**
  - `update` regenerates managed blocks against the current plan (still asks before writing).
  - `improve` audits the existing system and proposes a checklist of targeted fixes — user picks which to apply.
  - `replicate` ports an existing system from one runtime to others using the [Canonical IR](./references/replication.md#1-canonical-ir).

## Anti-patterns

- Writing files before showing the plan.
- Writing MCP config without explicit `ask_user` approval.
- Bulk-applying recommendations without per-item rationale + choice.
- Mixing platform frontmatters (e.g., Copilot keys in a Claude agent file).
- **Pairwise replication code** (Copilot→Claude function, Claude→OpenCode function, …) — always go through the [Canonical IR](./references/replication.md).
- Replicating without re-triggering the MCP approval gate for the new target(s).
- Symlinking `CLAUDE.md` on Windows (use the `.ps1` fallback-copy path).
- Backslashes in generated Markdown paths — always forward slashes.
- Skipping `.gitattributes` — Windows users get CRLF in `*.sh` and break execution.
- Single monolithic agent (violates orchestrator + subagent rule).
- Overwriting existing `AGENTS.md` / `opencode.json` without `.bak`.
- Generic descriptions ("helps with code") — kills discovery.
- Inventing plugin/skill/MCP names. Always cite `[Tier · Vendor]` from [marketplaces](./references/marketplaces.md).
- **Sequential-only orchestrator** — must fan out parallel-safe subagents (see [parallelism](./references/parallelism.md)).
- **Treating Codex CLI as `AGENTS.md`-only.** Current Codex (per [openai docs](https://developers.openai.com/codex/subagents)) supports project-scoped subagents at `.codex/agents/<name>.toml`. Reserve `## <Name>` headings inside `AGENTS.md` for the orchestrator + project rules; emit specialized subagents as TOML files.
- **Forgetting Codex's required TOML fields.** Every `.codex/agents/<name>.toml` MUST have `name`, `description`, and `developer_instructions`. Missing any of the three = silent skip on load.
- **Skipping Phase 8 wrap-up** — denies users the curated add-on menu (Spec-Kit, evals, telemetry, security review). See [wrap-up](./references/wrapup.md).
- **Wrap-up as per-item round-robin** — must be a *single* multi-select prompt.
- **Citing unofficial sources in the wrap-up menu** — only vendor-official docs or the catalogs listed in [wrap-up](./references/wrapup.md).
- **Replication ledger as `.md` or inside any `agents/` directory.** The replication ledger and any other operational log MUST be written to `.agents-system-setup/replication.jsonl` (JSON Lines). A `.md` log inside `.claude/agents/` / `.codex/agents/` / `.opencode/agents/` / `.github/agents/` will be parsed as a malformed agent by the runtime loader. See [replication anti-patterns](./references/replication.md#5-anti-patterns).
- **Treating security or architecture as optional wrap-up only** — the governance baseline is part of planning and generation, not a postscript.
- **Generating pattern names without rationale** — every architecture/design-pattern decision needs alternatives, guardrails, and an ADR reference or `n/a` rationale.
- **Creating a security auditor with broad write access** — security review is read-mostly unless the plan grants tightly scoped remediation paths.

## Output Contract

```
✅ Mode: <init|update|improve|replicate>
✅ Platforms: <copilot-cli, claude-code, opencode, codex-cli>
✅ Detected footprint: <list of pre-existing artifacts, or "none">
✅ Files created: <count>     (per platform: <breakdown>)
✅ Files updated (with .bak): <count>
✅ Subagents: <list>
✅ Skills: <list>
✅ Plugins selected: <list with [Tier · Vendor] and /plugin install (or platform-equivalent)>
✅ Plugins skipped: <list>
✅ MCP servers: <selected list> (approval: <approve-all | selective | skipped>)
✅ Security & audit baseline: <present | n/a with rationale>
✅ Threat model: <present | n/a with rationale>
✅ Architecture decisions: <count + ADR refs, or n/a with rationale>
✅ Quality gates: <build/test/lint/security/supply-chain/architecture evidence>
✅ Project memory link: <symlink | copy | n/a>
✅ Git: <initialized | left untouched | already present>
✅ Wrap-up add-ons selected: <list with source URL, or "none">
✅ Wrap-up add-ons skipped: <list, or "none">
✅ Codex subagent files (if codex-cli target): <list of .codex/agents/*.toml, or "none">

# replicate mode adds:
✅ Source runtime: <copilot-cli | claude-code | opencode | codex-cli>
✅ Target runtimes: <list>
✅ Lossy field drops: <list per target>
✅ Round-trip verify: <pass | drift on <fields>>
✅ Replication ledger: <path>

# improve mode adds:
✅ Audit findings: <ok / warn / fail counts>
✅ Security findings: <ok / warn / fail / requires-human counts>
✅ Architecture findings: <ok / warn / fail / requires-human counts>
✅ Deltas applied: <count>
✅ Deltas skipped: <count>
✅ Requires-human: <count>

Try it:
  copilot          # then: "@orchestrator <task>"
  claude           # then: invoke a subagent
  opencode         # then: pick an agent
  codex            # then: /agent to switch threads; orchestrator + rules in AGENTS.md, subagents in .codex/agents/*.toml

Suggested next customizations:
  - <suggestion 1>
  - <suggestion 2>
```
