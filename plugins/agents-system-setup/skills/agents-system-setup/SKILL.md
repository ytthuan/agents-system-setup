---
name: agents-system-setup
description: 'Bootstrap, improve, or replicate compact multi-agent systems across Copilot CLI, Claude Code, OpenCode, OpenAI Codex (CLI + App), and Gemini CLI. Generates AGENTS.md, orchestrator/subagents, skills, governance matrices, and opt-in plugin/MCP recommendations. Uses Canonical IR, MCP approval gates, platform-correct formats, and context-optimized output profiles. Triggers: "set up agents", "scaffold AGENTS.md", "improve my agents", "audit agent setup", "architecture review", "security audit agents", "replicate agents", "configure copilot/claude/opencode/codex/gemini", "discover plugins/MCP".'
argument-hint: '[init | update | improve | replicate] (omit to auto-detect)'
---

# Setup Copilot Agents (multi-platform)

Scaffold or update a complete agent system for the current project across **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**, and/or **Gemini CLI**. Produces a canonical `AGENTS.md` (with **Directory Architecture**, **Agent Roster**, **Capability Matrix**, **Security & Audit Matrix**, **Threat Model**, and **Architecture / Design Decisions**), an **orchestrator + N subagents**, project-scoped **skills**, and **approved** plugins/MCP servers — derived from a structured interview.

## When to Use

- Brand-new repository needs an agent setup from scratch (**init**)
- Existing project should adopt or extend the orchestrator + subagent pattern (**update**)
- Existing agent system needs an audit and targeted upgrades (**improve**)
- Agents authored for one runtime need to be ported to another (**replicate** — Copilot ↔ Claude Code ↔ OpenCode ↔ OpenAI Codex ↔ Gemini)
- Discovering relevant plugins / MCP servers from the well-known marketplaces

## Hard Rules

1. **Always interview first** with `ask_user`. Never assume project type, language, scope, or target platform.
2. **Detect existing agent footprint on entry.** If any of `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `opencode.json`, `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `.codex/agents/`, `.gemini/agents/`, `~/.codex/AGENTS.md` exists, present mode choice with `improve` and `replicate` as first-class options — never silently jump to `update`.
3. **Orchestrator + subagent topology is mandatory.** Subagent count (3 to ~50) is decided dynamically from scope.
4. **Directory Architecture is generated and enforced.** Every subagent file references it; the orchestrator routes by ownership.
5. **Per-item opt-in recommendations.** Plugin / skill / MCP candidates are always presented with rationale and explicit `ask_user` choice — never bulk-applied silently.
6. **MCP config approval gate.** Before writing any MCP config (`.mcp.json`, `opencode.json` › `mcp`, agent `mcp-servers:` / `mcp_servers:`, extension/plugin MCP manifests), render the proposal and call `ask_user` for approval. No silent MCP writes — ever. Replication re-triggers this gate per new target.
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
18. **Context budget is a feature.** Default to the `Balanced` output profile from [context optimization](./references/context-optimization.md): keep routing and gates inline, move deep detail behind explicit references, and never duplicate long policy prose in every agent.
19. **Ask whether agent artifacts are git-tracked or local-only.** Before writing project-scoped agent files, ask the tracking question from [local tracking](./references/local-tracking.md). For local-only project files, write `.git/info/exclude` (never `.gitignore`) and verify with `git check-ignore`.
20. **Plan handoff is normalized before emission.** Treat VS Code `plan` prompt output, Spec-Kit `/plan`, and user-written plans as upstream planning input only. Convert them to the [handoff contract](./references/handoff.md) / HandoffIR, then emit each selected runtime's native format. Never copy prompt frontmatter or another runtime's agent schema into generated artifacts.
21. **Runtime drift is source-backed and gated.** Use [runtime updates](./references/runtime-updates.md) before changing platform support. Gemini CLI is supported for local project subagents; remote A2A/extension packaging surfaces remain explicit import/package work.
22. **Model overrides are optional and source-backed.** Keep `model:` blank by default. Only when the user opts in during interview Q9b, load [models](./references/models.md) for the runtime's accepted format, defaults, and rate-limit sources. Never pin live RPM/TPM numbers in generated files.
23. **Task assignments use the canonical contract.** Compose every orchestrator → subagent handoff with the [Task Assignment Contract](./references/handoff.md#delegation-packet-canonical-schema). Always fill the Required Minimum; add Expansion Blocks per the [Recommended Packet Form](./references/handoff.md#recommended-packet-form). Subagents run the Acceptance Checklist before doing work and emit results via the Reporting Template; missing required fields trigger one consolidated `clarification_request:` to the orchestrator.

## Procedure

### Phase 0 — Platform Selection

First question after detecting cwd. Use `ask_user`:

> "Which agent runtime(s) should I configure?"
> Choices: `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex only (CLI + App artifacts)", "Gemini CLI only", "Copilot CLI + Claude Code", "All supported runtimes (Copilot + Claude Code + OpenCode + Codex + Gemini)"]`

Persist the selection. All later phases loop over selected platforms using [platforms.md](./references/platforms.md) as the source of truth for paths and frontmatter.

Gemini CLI emits local subagents at `.gemini/agents/*.md`. See [platforms](./references/platforms.md) and [agent format](./references/agent-format.md) for its non-recursive subagent and `mcp_servers:` rules.

### Phase 1 — Detect & Choose Mode

1. **Inspect cwd** and detect runtime footprint:
   - Project files: `package.json`, `*.csproj`, `Package.swift`, `build.gradle`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `mkdocs.yml`, `.git/`.
   - Agent artifacts (per runtime):
     - Copilot CLI: `AGENTS.md`, `.github/agents/*.agent.md`, `.github/agents/*.md` (docs-drift import signal), `.github/skills/`, `.mcp.json`
     - Claude Code: `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/settings.json`
     - OpenCode: `opencode.json`, `.opencode/agents/`, `.opencode/skills/`
     - OpenAI Codex: `AGENTS.md` (orchestrator + project rules), `.codex/agents/*.toml` (specialized subagents), `.codex/config.toml`, `~/.codex/AGENTS.md`, `~/.codex/agents/`; CLI-only plugin/command UX stays documented separately
     - Gemini CLI: `GEMINI.md`, `.gemini/agents/*.md`, `.gemini/settings.json`, `~/.gemini/GEMINI.md`, `~/.gemini/agents/`
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
5. Run **Phase 1.6** before any target write.
6. Re-run **Phase 3.5** MCP approval gate against each new target.
7. Emit per target with `<!-- agents-system-setup:replicated-from: <source> -->` markers.
8. Write replication ledger to `.agents-system-setup/replication.jsonl` (one JSON object per line — **never `.md`, never inside any `agents/` directory**, or it will be misread as a malformed agent).
9. Verify round-trip (re-parse emitted → diff IR → surface drift).

For **improve**, run Phase 1.6 before applying any selected delta. For both branches, finish with Phase 7 (verify & summarize).

### Phase 1.6 — Artifact Scope & Tracking

Run before Phase 1.7 for init/update, and before Phase 5 writes for improve/replicate. Use [local tracking](./references/local-tracking.md).

Ask:

> "Should the generated agent system be shared through git or kept local to this checkout?"
> Choices: `["Project files, git-tracked (Recommended for teams)", "Project files, local-only / untracked (Recommended for personal setup)", "Personal/global outside this repo"]`

Record `artifact_tracking` as `project-tracked | project-local | personal-global`.

Rules:
- `project-tracked`: use project paths; do not commit unless Phase 6 git actions are explicitly approved.
- `project-local`: use project paths, then add only generated/modified artifact paths to `.git/info/exclude` if `.git/` exists. Do not modify `.gitignore` for this.
- `personal-global`: use runtime user paths and avoid repo writes unless separately approved.

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

### Phase 1.9 — Output Profile & Context Budget

Run after Phase 1.8 and before Phase 2. Use [context optimization](./references/context-optimization.md).

Ask once:

> "How much detail should generated agent files include?"
> Choices: `["Balanced (Recommended)", "Compact", "Full"]`

Record:

- `output_profile`: `balanced | compact | full`
- `inline_sections`: which sections stay in `AGENTS.md`
- `overflow_targets`: where long details should be written or proposed (for example `docs/agents/security-audit.md`)
- `context_budget_notes`: any user constraints on verbosity

If the user is unsure, choose `Balanced`. This keeps all routing, ownership, governance, and quality gates inline while moving long rationale and overflow candidate lists to references.

### Phase 2 — Plan (Directory Architecture, Roster, Matrix, Waves)

Build the plan and show it before writing anything. The plan must include:

- **Directory Architecture** — table of `path glob | purpose | owner agent | edit rule`. Derived from project type + frameworks. Always covers: source dirs, tests, docs, infra, agent files, generated artifacts.
- **Agent Roster** — table of `name | role | owns | triggers | model (optional) | parallel-safe | wave`. Use [topology guide](./references/topology.md). Compute parallel-safety per [parallelism](./references/parallelism.md): a subagent is parallel-safe iff its `owns` glob doesn't overlap any other's, it doesn't write outside `owns`, and it doesn't depend on another subagent's output in the same wave.
- **Capability Matrix** — capabilities × agents grid (✅ / 🟡).
- **Wave plan** — grouped list `Wave N → [parallel-safe subagents]`; the orchestrator fans out per wave and awaits each before the next.
- **Plan Handoff Contract** — accepted planning sources, HandoffIR fields, per-platform format targets, approval boundaries, and verification evidence. Use [handoff](./references/handoff.md).
- Skills to create.
- Plugin/MCP candidates **per capability** (Phase 3 fills this).
- Per-platform file plan (Copilot/Claude/OpenCode/Codex/Gemini paths the user will actually get).
- **Artifact tracking** — `project-tracked | project-local | personal-global`, plus exclude plan for local-only mode.
- Git actions (if any).
- **Output profile & context budget** — `balanced|compact|full`, sections kept inline, overflow targets, and biggest expected agent-memory file.
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
   - Copilot CLI → `.mcp.json` (`mcpServers` key) and any approved agent-frontmatter `mcp-servers:`
   - Claude Code → `.mcp.json` (`mcpServers` key) and any approved project/user-agent `mcpServers`
   - OpenCode → merge into `opencode.json` (`mcp` key)
   - OpenAI Codex → `.mcp.json` plus any approved per-agent TOML `[mcp_servers.<id>]`
   - Gemini CLI → approved per-agent `mcp_servers:` blocks in `.gemini/agents/*.md`
2. Render each proposed file/config block verbatim (full JSON/YAML/TOML as applicable).
3. `ask_user`:
   > "I'm about to write the MCP configuration above to `<paths>`. Approve?"
   > Choices: `["Approve all (Recommended)", "Approve selectively (per-server)", "Skip MCP entirely"]`
4. If **selective**, loop per server: `["Include", "Skip"]`.
5. If **skip**, strip every `mcp-servers:` / `mcpServers` / `mcp_servers:` / TOML `[mcp_servers.*]` surface from generated agents and do not write `.mcp.json` / `opencode.json` `mcp` / extension MCP config.
6. **No MCP write may occur before this gate returns approval.**

### Phase 4 — Generate Artifacts (per platform, post-approval)

For each selected platform, look up paths and frontmatter in [platforms.md](./references/platforms.md), then render:

- `AGENTS.md` at repo root → [template](./assets/AGENTS.md.template). Fill **Read First**, **Context Loading Policy**, **Directory Architecture**, **Agent Roster**, **Capability Matrix**, **Plan Handoff Contract**, **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, **Quality Gates**, **Skills**, **Plugins/MCP** tables. Use the selected output profile from Phase 1.9; summarize long sections and link overflow details instead of dumping exhaustive prose inline.
- `GEMINI.md` when Gemini CLI is selected → [template](./assets/GEMINI.md.template). Keep it a compact pointer/sync copy that tells Gemini to load canonical `AGENTS.md`, preserves artifact tracking notes, and routes root-session fan-out because Gemini subagents cannot recursively delegate.
- Orchestrator — use the **platform-specific template**:
  - **Copilot CLI** → [orchestrator.agent.md.template](./assets/orchestrator.agent.md.template) at `.github/agents/orchestrator.agent.md`.
  - **Claude Code** → [orchestrator.claude.md.template](./assets/orchestrator.claude.md.template) at `.claude/agents/orchestrator.md`. Frontmatter uses `name` + `description`; `tools:` is a comma-separated string; no `mcp-servers:` key (MCP lives in `.mcp.json`).
  - **OpenCode** → [orchestrator.opencode.md.template](./assets/orchestrator.opencode.md.template) at `.opencode/agents/orchestrator.md`. Frontmatter has **no `name:`** (filename is the name); `mode: primary`; model uses `provider/model-id` format; MCP stays in `opencode.json`.
  - **OpenAI Codex (CLI + App)** → `## Orchestrator` heading in `AGENTS.md` (orchestrator and project rules live there; specialized subagents are TOML files).
- Each subagent — use the **platform-specific template** and fill `{{OWNED_PATHS}}` / `{{READONLY_PATHS}}` from the Directory Architecture:
  - **Copilot CLI** → [subagent.agent.md.template](./assets/subagent.agent.md.template) at `.github/agents/<name>.agent.md`. Frontmatter: `name`, `description`, `tools:` list filled from the [Standard Tool Profile](./references/platforms.md#copilot-cli-standard-tool-profiles) per role (orchestrator + edit-capable subagents → `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors → `[read, search]`; testers/release helpers → `[execute, read, search, todo]`; research/docs → `[read, search, web, todo]`; or omit when the user picked `inherit`), optional `mcp-servers:` (hyphenated key). `.github/agents/<name>.md` is recognized only as an upstream docs-drift/import signal, not the default emitter.
  - **Claude Code** → [subagent.claude.md.template](./assets/subagent.claude.md.template) at `.claude/agents/<name>.md`. Frontmatter: `name`, `description`, optional `tools:` as **comma-separated string** (e.g. `Read, Grep, Bash`), optional `disallowedTools:`, `permissionMode:`, `model:`, etc. Do **not** use Copilot tool names or `mcp-servers:`.
  - **OpenCode** → [subagent.opencode.md.template](./assets/subagent.opencode.md.template) at `.opencode/agents/<name>.md`. Frontmatter: **no `name:`** (filename = agent name), `description`, `mode: subagent`, optional `model:` in `provider/model-id` format, optional `permission:` block. Do **not** embed `mcp-servers:` — MCP belongs in `opencode.json`.
  - **OpenAI Codex (CLI + App)** → [subagent.codex.toml.template](./assets/subagent.codex.toml.template) at `.codex/agents/<kebab-name>.toml`. Required fields: `name`, `description`, `developer_instructions` (TOML triple-quoted string). Carry the IR's `tool_allowlist` only if explicitly set (otherwise inherit from parent session). Map IR `model` → `model` and reasoning hints → `model_reasoning_effort` (`low`|`medium`|`high`). Set `sandbox_mode = "read-only"` for read-only subagents. Per-agent MCP servers go under `[mcp_servers.<id>]` in the same file. `AGENTS.md` keeps only the orchestrator section + Directory Architecture / Capability Matrix / Waves. See [Codex layout](./references/platforms.md) and [openai docs](https://developers.openai.com/codex/subagents). CLI-only instructions such as `/agent` are usage notes, not requirements for App compatibility. Also emit/upsert `.codex/config.toml` with `[agents] max_threads = 6` and `max_depth = 1` unless the user supplied other values.
  - **Gemini CLI** → [subagent.gemini.md.template](./assets/subagent.gemini.md.template) at `.gemini/agents/<kebab-name>.md`. Required fields: `name`, `description`; emit `kind: local`; optional `display_name`, `tools`, `mcp_servers`, `model`, `temperature`, `max_turns`, `timeout_mins`. Use snake_case `mcp_servers:` only after Phase 3.5 approval. Gemini subagents cannot call other subagents, so cross-agent work returns to the orchestrator/root session.
- Each skill → [template](./assets/skill.template.md) at the platform's skills path.
- MCP config (only if Phase 3.5 approved) at the platform's MCP path.
- Drop the [directory-architecture snippet](./assets/directory-architecture.snippet.md) into any agent missing the boundary block.
- **Orchestrator parallelism clause** — render the wave-aware fan-out instructions per [parallelism](./references/parallelism.md). The orchestrator must invoke all parallel-safe subagents of a wave in a single response (multiple Task-tool calls), await all results, then start the next wave.
- **Plan handoff contract** — render the HandoffIR fields and platform format targets per [handoff](./references/handoff.md). Agent files receive a concise handoff input/output section; Codex subagents receive it inside `developer_instructions`.
- **Governance baseline** — render the security, audit, architecture, design-pattern, ADR, and quality-gate sections from Phase 1.8 / Phase 2. Subagents that touch sensitive paths, MCP/tool config, CI/release config, dependency manifests, or architecture boundaries must include explicit security boundaries and audit evidence expectations.
- **Context optimization** — apply [context optimization](./references/context-optimization.md): compact inline summaries, links for overflow details, concise delegation packets, no duplicated long policy prose across subagents, and **profile-aware compact-mode trimming** for Compact subagents (Security/Architecture/Output sections collapse to one line + link; section anchors stay so validators can find them). Codex TOML always follows the [summary + pointer rule](./references/agent-format.md#codex-toml-summary--pointer-rule). Set `Context freshness: recent` in delegation packets when `AGENTS.md` was loaded this turn.
- **Artifact tracking** — apply [local tracking](./references/local-tracking.md). In `project-local` mode, update `.git/info/exclude` after writes and verify at least `AGENTS.md` with `git check-ignore -v`.
- **Spec-Kit block** — if Phase 1.7 recorded `spec_kit_installed = true`, render `assets/spec-kit-block.snippet.md` into the `{{SPEC_KIT_BLOCK}}` placeholder of `AGENTS.md` (substituting `{{RUNTIME}}` per platform: `copilot|claude|codex|opencode|gemini`). If `false`, replace the placeholder with an empty string. See [spec-kit](./references/spec-kit.md).
- **Claude Code AGENT-TEAMS.md** — when Claude Code is among the selected platforms AND the Agent Roster has 3+ subagents marked `team-suitable` (independent + benefits from peer challenge), emit `AGENT-TEAMS.md` documenting: opt-in env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), settings.json snippet, suggested teammate roster, token-cost warning, and when to fall back to parallel subagents.

**Project-memory linking** (after AGENTS.md is written):
- If both Claude Code and another platform are selected → pick by detected OS (see [cross-platform](./references/cross-platform.md)):
  - **macOS / Linux / WSL**: `bash ./scripts/link-project-memory.sh` → symlinks `CLAUDE.md → AGENTS.md`.
  - **Windows native**: `pwsh -File ./scripts/link-project-memory.ps1` → tries symlink (Developer Mode/admin), falls back to copy with regenerable header (re-runs keep them in sync).
- OpenCode reads `AGENTS.md` natively — no linking required.
- Gemini CLI uses `GEMINI.md` as its native context file; when Gemini is selected, keep `GEMINI.md` a compact pointer/sync copy of canonical `AGENTS.md` (same OS-specific symlink/copy caution as Claude).

**Frontmatter rules** (silent-failure traps):
- `name` MUST match filename basename (kebab-case).
- Quote any `description` containing colons.
- Subagent `description` MUST start with `"Use when..."`.
- Use the **right frontmatter schema per platform** (see [platforms.md](./references/platforms.md) — Copilot uses `mcp-servers:` and public tool aliases (`vscode`, `execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`), Claude uses comma-string `tools:`, OpenCode uses `mode:` plus `permission:`, Codex subagents use `.toml`, and Gemini uses `kind: local` plus `mcp_servers:`).
- Restrict tools per subagent to the minimum needed. For Copilot CLI, apply the Phase 4 Role → Profile mapping from [Copilot CLI Standard Tool Profiles](./references/platforms.md#copilot-cli-standard-tool-profiles) (Q9c override wins; default `Standard`).
- The `model:` line is optional in every platform — emit only if the user specified an override. When users opt in to overrides during interview Q9b, load [models](./references/models.md) for the runtime's accepted format, defaults, and rate-limit sources; never pin live RPM/TPM numbers in generated files.

### Phase 5 — Update Mode (non-destructive)

For every existing target file:
1. `cp <file> <file>.bak` via bash before any edit.
2. Parse existing frontmatter; preserve user-authored sections.
3. Merge new content under `<!-- agents-system-setup:managed:start -->` … `<!-- agents-system-setup:managed:end -->` markers — replace the block, never duplicate.
4. If `artifact_tracking == project-local`, add only generated/modified artifact paths to `.git/info/exclude` and verify with `git check-ignore -v`.
5. Print a diff summary at the end.

### Phase 6 — Optional Git Init

Only if user confirmed in Phase 1 AND no `.git/` exists. Pick the script that matches the host OS — see [cross-platform](./references/cross-platform.md). The bundled scripts initialize `main`, write `.gitignore` and `.gitattributes`, stage, and commit.

### Phase 7 — Verify & Summarize

1. List every file created/modified with absolute paths, grouped by platform.
2. Re-read each generated agent/skill: confirm `name` matches filename (Copilot, Claude Code, Gemini CLI), no `name:` key in OpenCode files (filename is the name), `description` present and starts with `"Use when..."`, no unquoted colons, frontmatter parses for the *target platform's* schema. Confirm Claude Code `tools:` is a comma-separated string — not a YAML list. Confirm OpenCode files have no `mcp-servers:` key. Confirm Gemini files use `mcp_servers:` (not `mcpServers`) and do not instruct subagents to call subagents. Confirm no `agent: Plan` frontmatter was copied into any generated file.
3. Verify `AGENTS.md` contains non-empty **Directory Architecture**, **Agent Roster**, **Capability Matrix**.
4. Verify `AGENTS.md` contains non-empty **Security & Audit Matrix**, **Threat Model**, **Architecture / Design Pattern Decisions**, **ADR Index**, and **Quality Gates**. If a concern is not applicable, it must still have an explicit `n/a` rationale.
5. Verify security-sensitive files (`.mcp.json`, `opencode.json`, `.env*`, CI/release config, lockfiles, generated scripts) have an owner and evidence requirement in the governance sections.
6. Verify `AGENTS.md` contains **Plan Handoff Contract**, **Context Loading Policy** (including the **Task-Type Routing Map** rows), and records the selected output profile.
7. Verify every generated agent/subagent uses its target runtime's native handoff surface: Markdown body for Copilot/Claude/OpenCode/Gemini, TOML `developer_instructions` for Codex. Confirm each subagent template includes the **Acceptance Checklist** and **Reporting Template** sections; Codex TOML mirrors them inside `developer_instructions`. For Copilot CLI agents, confirm the `tools:` line matches the role's profile from [Copilot CLI Standard Tool Profiles](./references/platforms.md#copilot-cli-standard-tool-profiles): orchestrator + edit-capable subagents emit `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors emit `[read, search]`; the marker `<!-- agents-system-setup:tools-profile: <profile> -->` records the chosen profile.
8. Verify artifact tracking: project-tracked files are visible to git; project-local files are ignored via `.git/info/exclude`; personal-global mode wrote no repo artifacts unless approved.
9. Print "Try it" examples per selected platform (`copilot`, `claude`, `opencode`, `codex`, `gemini`).
10. Suggest 2–3 next customizations.

### Phase 8 — Final Wrap-Up (single consolidated ask)

Run after Phase 7, **before** exiting. Present one compact multi-select menu from [wrap-up](./references/wrapup.md), filtered by domain/plugins/MCP/platform signals. Never show installed items; never ask one item at a time. Re-confirm only if an action edits config outside `AGENTS.md`.

Skip the entire phase only when `mode == update` and no agents/plugins/MCP changed.

## Decision Aids

- **How many subagents?** [topology guide](./references/topology.md). One subagent per durable concern — also a path owner in the Directory Architecture.
- **Skill vs Subagent?** Reusable workflow with assets → Skill. Context isolation / different tool restrictions → Subagent.
- **Plugin vs MCP?** Plugins extend the runtime; MCP servers expose tools to agents. External-system integrations are usually MCP.
- **Dedicated security/architecture agent or merged role?** Dedicated when the repo handles sensitive data, external tools/MCP, CI/release, regulated domains, monorepos, or user-requested architecture work. Merge into `@reviewer` only for small projects, and keep explicit ownership in the Security & Audit Matrix.
- **Compact vs balanced vs full output?** Balanced by default. Compact for experienced teams or small repos. Full only for onboarding, audit, or when the user explicitly asks for exhaustive detail. See [context optimization](./references/context-optimization.md).
- **Git-tracked or local-only?** Teams usually want `project-tracked`; personal experimentation should use `project-local` with `.git/info/exclude`; reusable private agents should use `personal-global`.
- **Which platform?** Copilot CLI for GitHub-tight teams; Claude Code for Anthropic-first; OpenCode for vendor-neutral / self-hosted; OpenAI Codex for OpenAI-first teams (CLI + App compatible artifacts, using split layout: `AGENTS.md` for orchestrator + rules, `.codex/agents/*.toml` for specialized subagents); Gemini CLI for Google/Gemini-first terminal workflows using `.gemini/agents/*.md`. Multi-target if uncertain — files coexist cleanly via shared `AGENTS.md` + runtime-specific subagent dirs.
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
- **Treating Codex as `AGENTS.md`-only.** Current Codex (per [openai docs](https://developers.openai.com/codex/subagents)) supports project-scoped subagents at `.codex/agents/<name>.toml`, with subagent activity surfaced in both the Codex app and CLI. Reserve `## <Name>` headings inside `AGENTS.md` for the orchestrator + project rules; emit specialized subagents as TOML files.
- **Forgetting Codex's required TOML fields.** Every `.codex/agents/<name>.toml` MUST have `name`, `description`, and `developer_instructions`. Missing any of the three = silent skip on load.
- **Skipping Phase 8 wrap-up** — denies users the curated add-on menu (Spec-Kit, evals, telemetry, security review). See [wrap-up](./references/wrapup.md).
- **Wrap-up as per-item round-robin** — must be a *single* multi-select prompt.
- **Citing unofficial sources in the wrap-up menu** — only vendor-official docs or the catalogs listed in [wrap-up](./references/wrapup.md).
- **Replication ledger as `.md` or inside any `agents/` directory.** The replication ledger and any other operational log MUST be written to `.agents-system-setup/replication.jsonl` (JSON Lines). A `.md` log inside `.claude/agents/` / `.codex/agents/` / `.opencode/agents/` / `.github/agents/` will be parsed as a malformed agent by the runtime loader. See [replication anti-patterns](./references/replication.md#5-anti-patterns).
- **Treating security or architecture as optional wrap-up only** — the governance baseline is part of planning and generation, not a postscript.
- **Generating pattern names without rationale** — every architecture/design-pattern decision needs alternatives, guardrails, and an ADR reference or `n/a` rationale.
- **Creating a security auditor with broad write access** — security review is read-mostly unless the plan grants tightly scoped remediation paths.
- **Using verbosity as safety** — long repeated prompts do not make agents safer. Keep gates and ownership inline, link detail, and require evidence.
- **Hiding overflow details** — any moved detail must be linked from `AGENTS.md` or listed in the output contract.
- **Assuming agent artifacts should be committed** — always ask tracking mode before writing project files.
- **Using `.gitignore` for local-only project agents without approval** — local-only mode belongs in `.git/info/exclude`.
- **Copying plan prompt frontmatter into agent files** — the VS Code `plan` prompt (`agent: Plan`) is an upstream planning surface, not a runtime agent schema. Normalize to HandoffIR, then emit per-platform formats.
- **Letting Gemini subagents recurse** — Gemini subagents cannot call other subagents; route fan-out through the parent/orchestrator session.
- **Using Gemini's docs-spelled `mcpServers` in local subagents** — generated local agents must use loader-valid `mcp_servers:` and must pass the MCP approval gate.

## Output Contract

Use [output-contract](./references/output-contract.md). Always include `Context profile`, `Context split`, and largest memory file. For `Compact` and `Balanced`, lead with counts, changed paths, security/architecture evidence, and "Try it" commands; expand full lists only for failures, warnings, or explicit user requests.
