# Changelog

All notable changes to this plugin are documented here. Format: [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

### Added

- **Copilot CLI Standard Tool Profile.** Generated Copilot CLI agents now apply a documented role-aware tool profile: `standard` (`tools: [vscode, execute, read, agent, edit, search, todo]`) for orchestrator and edit-capable subagents, `read-only` (`[read, search]`) for reviewers/auditors, `runner` (`[execute, read, search, todo]`) for testers, `research` (`[read, search, web, todo]`) for docs/research gatherers, and `inherit` (omit `tools:`) for explicit opt-out.
- `vscode` added to the recognized public alias set in `references/platforms.md` and `references/agent-format.md`. The `vscode` tool exposes the VS Code chat-host tool set when the agent runs inside VS Code Chat; Copilot CLI ignores unknown aliases harmlessly per the documented "All unrecognized tool names are ignored" rule, so it ships safely as a baseline.
- New interview question Q9c (`copilot_tools_profile`) lets users pick `Standard | Minimal | Custom | Inherit`. Default = Standard.
- Output contract reports the chosen profile via `Copilot CLI tools profile:`.
- Validator guardrail `check_copilot_tool_profile` keeps the standard tool profile, marker `<!-- agents-system-setup:tools-profile: <profile> -->`, and orchestrator-must-have-`agent` rule from regressing.

### Changed

- Replication into Copilot CLI now fills `tools:` from the role-derived profile when the source IR has no explicit tools list; user-set tool lists still pass through unchanged. Tool-name canonicalization adds a `vscode_host → vscode` row.
- Orchestrator template always renders `tools: [vscode, execute, read, agent, edit, search, todo]`. Subagent template documents the role → profile mapping and records the chosen profile via `<!-- agents-system-setup:tools-profile: {{TOOLS_PROFILE}} -->`.

## [0.7.0] - 2026-04-27

### Added

- Plan Handoff Contract guidance normalizes VS Code Plan agent output, Spec-Kit `/plan`, and user-written plans into HandoffIR before runtime-specific emission.
- Generated `AGENTS.md`, orchestrator, Markdown subagent, and Codex TOML templates now include concise handoff input/output fields.
- Validator guardrail `check_plan_handoff_policy` keeps the handoff reference, template markers, and output contract from regressing.
- Validator guardrail `check_codex_cli_app_compatibility` keeps Codex setup and replication docs compatible with shared CLI + App artifacts without overclaiming App plugin installation.

### Changed

- Platform references now consistently describe four runtimes and clarify OpenCode's `permission:`-based agent schema.
- Codex setup, replication, templates, output contract, and README now distinguish shared **OpenAI Codex CLI + App** artifacts from CLI-only plugin and slash-command workflows.
- `AGENTS.md` templates now name OpenAI Codex as a native project-memory consumer alongside Claude Code and OpenCode.

## [0.8.0] - 2026-04-30

### Added

- Public docs now present five supported runtimes: Copilot CLI, Claude Code, OpenCode, OpenAI Codex (CLI + App), and Gemini CLI artifact support.
- Runtime Update Audit reference tracks latest upstream format drift for Copilot CLI, Claude Code, OpenCode, OpenAI Codex, and Gemini CLI support.
- Validator guardrails keep runtime drift notes, supported-vs-candidate status, and refreshed schema markers from regressing.
- Per-runtime model constraints reference (`references/models.md`) documents accepted `model:` formats, defaults, and source-linked rate-limit pointers; interview Q9b stays optional and points at the new reference.
- Output contract now records `Model overrides:` (none vs per-agent overrides) so users can see at a glance whether runtime defaults or explicit ids are in effect.
- Context engine sharpened: `references/handoff.md` is now the single source of truth for the Delegation Packet; orchestrator templates and `references/context-optimization.md` link to it instead of restating the schema. New Task-Type Routing Map and context-freshness rule cut redundant reads, and a Codex TOML "summary + pointer" rule keeps `developer_instructions` compact. Output contract now reports a `Context budget` line with measured surface sizes.
- Validator adds warn-only context-budget checks for AGENTS.md template Read First length, Codex `developer_instructions` line count, and managed-block drift across re-runs.
- Task Assignment Contract: orchestrator → subagent handoff schema expanded with Required Minimum + opt-in Expansion Blocks (Goal & Definition of Done, Scope, File Inventory, Background, Reproduction, Constraints, Assumptions, Known Risks, Verification Protocol, Reporting Protocol, Coordination, Size & Timebox, Clarification Protocol). Subagent templates now include Acceptance Checklist + Reporting Template; Codex TOML mirrors both inside `developer_instructions`. Output contract records `Task assignment quality:` and `Clarifications requested:`.

### Changed

- Copilot guidance now records the `.agent.md` vs `.md` documentation drift while keeping `.agent.md` as the emitted format.
- Claude Code guidance now distinguishes project/user/session subagent fields from plugin-shipped agent field restrictions.
- OpenCode guidance now prefers `permission:` over deprecated `tools:` and lists the current permission key set.
- Codex guidance now covers `job_max_runtime_seconds`, `spawn_agents_on_csv`, richer plugin component references, apps, and marketplace metadata.
- README and DESIGN now describe Gemini CLI as artifact-first support and explicitly avoid inventing a Gemini plugin install path.

## [0.6.1] - 2026-04-25

### Added

- New `references/local-tracking.md` documents `project-tracked`, `project-local`, and `personal-global` artifact modes.
- Interview flow now asks whether generated agent artifacts should be git-tracked, local-only for the current checkout, or written to personal/global runtime paths.
- Generated `AGENTS.md` template records artifact tracking mode and local-tracking notes.
- Output contract now reports artifact tracking and local exclude status.
- Validator guardrail `check_local_tracking_policy` prevents removing the local-vs-git-tracked policy, interview question, template placeholders, and output markers.

### Changed

- `SKILL.md`, README, and DESIGN now make artifact tracking an explicit write-time decision.
- Local-only project artifacts use `.git/info/exclude` instead of `.gitignore`, with `git check-ignore` verification.

## [0.6.0] - 2026-04-25

### Added

- **Context optimization baseline.** New `references/context-optimization.md` defines output profiles (`Balanced`, `Compact`, `Full`), generated-output hierarchy, context budgets, inline-vs-reference split, concise delegation packets, and anti-patterns.
- New `assets/context-loading-policy.snippet.md` for consistent generated `AGENTS.md` context-loading guidance.
- New `references/output-contract.md` moves the verbose completion contract out of always-loaded `SKILL.md`.
- New Phase 1.9 in `SKILL.md`: Output Profile & Context Budget.
- New validator pass `check_context_optimization` requires the context optimization reference, generated-template markers, load-order guidance, concise-output guidance, and warns if `SKILL.md` grows beyond the target size.

### Changed

- `SKILL.md` frontmatter description shortened and made trigger-focused; body reduced below the context-budget target by moving the full output contract to a reference.
- Generated `AGENTS.md` template now includes **Read First**, **Context Loading Policy**, `{{CONTEXT_PROFILE}}`, `{{DETAIL_REFERENCES}}`, and overflow placeholders for large matrices.
- Orchestrator template now includes context load order and concise delegation-packet format.
- Subagent and Codex TOML templates now include load-order and concise output guidance without duplicating full project policy.
- Interview flow now asks the user to choose `Balanced (Recommended)`, `Compact`, or `Full` detail.
- Governance, replication, wrap-up, and plugin-discovery references now explicitly support compact inline summaries with linked overflow detail.
- README and DESIGN updated to document compact-by-default generated output.

### Fixed

- Prevented the previous large Output Contract block from inflating always-loaded `SKILL.md` context.

## [0.5.0] - 2026-04-25

### Added

- **Mandatory security, audit, design-pattern, and architecture governance baseline.** Generated systems now plan and emit:
  - Security & Audit Matrix
  - Threat Model
  - Architecture / Design Pattern Decisions
  - ADR Index
  - Quality Gates
- New reference: `references/security-audit-architecture.md`, source-backed by OWASP GenAI Security, NIST SSDF, MCP Security Best Practices, GitHub Code Security, SLSA, Open Policy Agent, Azure Well-Architected Framework, C4 Model, and TOGAF (enterprise-only framing).
- New Phase 1.8 in `SKILL.md`: Security, Audit, Architecture Intake.
- New validator guardrail `check_governance_baseline` ensures required governance references and template sections cannot be removed accidentally.

### Changed

- `SKILL.md` hard rules, procedure, output contract, decision aids, and anti-patterns now treat governance as a first-class generation gate, not a final optional wrap-up.
- `references/interview.md` adds focused questions for data sensitivity, auth boundary, external tools/MCP, audit evidence, architecture style, quality attributes, and design anti-patterns.
- `references/topology.md` now models governance ownership: `security-auditor`, `architecture-reviewer`, `design-pattern-reviewer`, optional `threat-modeler` / `compliance-auditor`, and merged-role guidance for small projects.
- `assets/AGENTS.md.template`, orchestrator, subagent, Codex TOML, and Directory Architecture snippets now include security boundaries, audit evidence, architecture decisions, ADRs, and quality gates.
- `references/replication.md` Canonical IR now preserves governance metadata (`security_controls`, `audit_requirements`, `architecture_decisions`, `quality_gates`, `sensitive_paths`) or reports lossiness.
- `references/marketplaces.md` and `references/wrapup.md` expanded with source-backed security/supply-chain/policy/architecture recommendations.
- `README.md` and `DESIGN.md` updated for the governance baseline and current plugin sub-tree layout.

### Fixed

- Removed a stale untracked root `skills/` skeleton before validation; canonical skill payload remains under `plugins/agents-system-setup/skills/agents-system-setup/`.

## [0.4.1] - 2026-04-23

### Fixed

- **Replication ledger no longer lands in an agents/ directory.** Previously the procedure wrote `.github/agent-replication.log` (or "platform-equiv"), which on Codex / Claude / OpenCode could end up adjacent to `agents/` trees. Worse, anyone hand-renaming the ledger to `.md` would have it parsed as a malformed agent by the runtime loader.
  - Ledger path is now pinned to **`.agents-system-setup/replication.jsonl`** at the repo root.
  - Format switched from free-form text → **JSON Lines** (`{"ts":..., "source":..., "targets":[...], "files":[{"path":..., "sha256":...}]}` per line).
  - **NEVER** allowed inside `.claude/agents/`, `.codex/agents/`, `.opencode/agents/`, `.github/agents/`, `~/.config/opencode/agents/`.
  - **NEVER** allowed with a `.md` extension inside any `agents/` tree.
- New validator pass `check_replication_ledger` in `scripts/_validate.py` enforces both rules and fails the build if violated.
- New anti-pattern entries added to `SKILL.md` § Anti-patterns and `references/replication.md` § 5.

### Changed

- `assets/gitignore.template` now ignores `.agents-system-setup/` (operational state — replication ledger, audit logs, `.bak` files) with an inline warning explaining why this directory must never sit inside an `agents/` tree.
- `references/replication.md` § 6 References: Claude Code subagents URL updated `docs.anthropic.com` → `docs.claude.com` (canonical home).

## [0.4.0] - 2026-04-23

### Added — `references/marketplaces.md` rewrite (verified 2026-04 via live GitHub search)

- **OpenAI official catalogs** added to Tier 1: `openai/skills` (Skills Catalog for Codex, ~17k★), `openai/plugins`, `openai/codex-plugin-cc` (Codex-from-Claude-Code bridge).
- **Anthropic** Tier 1 entries cleaned up.
- **OpenCode** ecosystem entry added to Tier 2: `awesome-opencode/awesome-opencode` (~5.5k★) — was missing previously.
- **Claude Code Tier 2 expanded** with verified high-signal repos:
  - `wshobson/agents` (~34k★) — multi-agent orchestration
  - `obra/superpowers` — agentic skills framework
  - `rohitg00/awesome-claude-code-toolkit` — 135 agents / 35 skills / 176+ plugins
  - `helloianneo/awesome-claude-code-skills` — 50+ scenario-grouped picks
  - `alexei-led/cc-thingz` — battle-tested marketplace
- **Cross-runtime catalogs** new section: `EveryInc/compound-engineering-plugin`, `numman-ali/n-skills`, `gmh5225/awesome-skills`, `safishamsi/graphify`.
- **Domain-specific skill packs** new section as prior-art reference: `dotnet/skills`, `kepano/obsidian-skills`, `microsoft/GitHub-Copilot-for-Azure`.

### Changed

- Doc anchors updated: Claude Code plugins doc moved to `docs.claude.com`; Codex plugins now split into separate "build" and "use" anchors; OpenCode anchor added.
- **Install patterns section** rewritten per-runtime with current commands (Codex `marketplace add ... --ref / --sparse`, `marketplace upgrade/remove`).
- **Cross-runtime cheat sheet** added (table mapping Agents / Skills / Hooks / MCP / LSP / Commands to each runtime's path).
- Vendor-attribution rule kept; tag format unchanged.

## [0.3.3] - 2026-04-23

### Changed

- **Marketplace identifier renamed** from `agents-system-setup` → `ytthuan` (owner handle) in both marketplace manifests:
  - `.agents/plugins/marketplace.json` (`name` + `interface.displayName`)
  - `.claude-plugin/marketplace.json` (top-level `name`)
- The plugin name itself (`agents-system-setup`) is unchanged in both files. Only the **marketplace** key is renamed so it no longer collides with the plugin name.
- **User impact (Codex CLI):** the local config block changes from `[marketplaces.agents-system-setup]` to `[marketplaces.ytthuan]`. Users who already added the marketplace can either:
  - Run `codex plugin marketplace remove agents-system-setup` then `codex plugin marketplace add ytthuan/agents-system-setup` to refresh, or
  - Edit `~/.codex/config.toml` and rename the section header from `[marketplaces.agents-system-setup]` to `[marketplaces.ytthuan]`.

## [0.3.2] - 2026-04-22

### Fixed

- Markdown lint error (MD028 — blank line inside blockquote) in `references/agent-format.md` introduced in v0.3.1; merged the two adjacent blockquotes into one. v0.3.1 release assets are functionally identical but tripped the markdownlint CI gate.

## [0.3.1] - 2026-04-22

### Changed

- **Claude Code subagent spec — full alignment with current docs** ([docs.claude.com/en/docs/claude-code/sub-agents](https://docs.claude.com/en/docs/claude-code/sub-agents)):
  - Source URL fixed (was `docs.anthropic.com`, now `docs.claude.com`).
  - Documented all optional frontmatter fields the skill previously omitted: `disallowedTools`, `permissionMode` (`default|acceptEdits|auto|dontAsk|bypassPermissions|plan`), `maxTurns`, `skills` (full content injected, NOT inherited from parent), `mcpServers` (name ref or inline), `hooks`, `memory` (`user|project|local`), `background`, `effort` (`low|medium|high|xhigh|max`), `isolation: worktree`, `color`, `initialPrompt`.
  - Clarified `model` accepts full model IDs (e.g. `claude-opus-4-7`) in addition to aliases; default is `inherit`.
  - Documented scope precedence: managed settings → `--agents` CLI JSON → `.claude/agents/` (project) → `~/.claude/agents/` (user) → plugin `agents/`. Higher-priority same-name overrides lower.
  - Documented `disallowedTools` ordering: applied before `tools`.
- **OpenCode subagent spec — full alignment with current docs** ([opencode.ai/docs/agents](https://opencode.ai/docs/agents)):
  - **`tools:` field is now flagged as deprecated**; `permission:` (with `edit` / `bash` / `webfetch` granularity) is the recommended path.
  - Removed misleading `mcp: []` example from frontmatter — OpenCode does not configure MCP in agent frontmatter; declare in `opencode.json` › `mcp`.
  - Added missing fields: `prompt` (file ref), `disable`, `hidden`, `color` (hex or theme), `top_p`, `steps` (max agentic iterations), `permission.task` (gate Task-tool subagent invocation), `permission.webfetch`.
  - Documented bash-permission ordering: wildcard FIRST, specific rules after (last match wins).
  - Documented built-in agents: primaries `build` + `plan`; subagents `general` + `explore`. Filename = agent name.
  - Noted that extra top-level keys (e.g. `reasoningEffort`, `textVerbosity`) pass through directly as provider model options.
- `references/replication.md` Field-Mapping Matrix updated: Claude `tools` cell now mentions `disallowedTools` denylist; OpenCode cell flips primary recommendation to `permission` and marks legacy `tools: { ... }` map as deprecated.

## [0.3.0] - 2026-04-22

### Added

- **Codex CLI native subagents.** The skill now generates one `.codex/agents/<name>.toml` per specialized subagent, matching OpenAI's current Codex subagents spec (https://developers.openai.com/codex/subagents). Required TOML fields wired through the canonical IR: `name`, `description`, `developer_instructions`. Optional fields (`model`, `model_reasoning_effort`, `sandbox_mode`, `nickname_candidates`, per-agent `[mcp_servers.<id>]`, `[[skills.config]]`) are emitted only when the IR sets them; otherwise the subagent inherits from the parent session.
- New asset `assets/subagent.codex.toml.template` with placeholders (`{{NAME}}`, `{{DESCRIPTION}}`, `{{DEVELOPER_INSTRUCTIONS}}`, `{{MODEL}}`, `{{REASONING_EFFORT}}`, `{{SANDBOX_MODE}}`, `{{MCP_ID}}`, `{{MCP_URL}}`, `{{SKILL_PATH}}`).
- New validator pass `check_codex_toml_agents` in `scripts/_validate.py`: parses every `.codex/agents/*.toml` under the repo via `tomllib`, enforces the three required fields, validates `model_reasoning_effort ∈ {low,medium,high}` and `sandbox_mode ∈ {read-only,workspace-write}`, and warns when TOML `name` ≠ filename stem.

### Changed

- **Codex generation flow split.** `AGENTS.md` is now reserved for project rules, Directory Architecture, Capability Matrix, Waves, and the orchestrator section only. Per-subagent `## <Name>` headings are no longer emitted for Codex targets — specialized workers live in `.codex/agents/*.toml` instead. `AGENTS.md` is still the primary project memory file Codex reads on session start.
- `.codex/config.toml` is upserted with `[agents] max_threads = 6` and `max_depth = 1` defaults when Codex is in the target set.
- `references/platforms.md` Codex section rewritten with the TOML schema, the `/agent` switching workflow, and the global `[agents]` config block.
- `references/agent-format.md` Codex section replaced; Tool Restriction Patterns table now shows Codex `sandbox_mode` instead of prose.
- `references/replication.md` Field-Mapping Matrix updated: `name` → TOML `name`, `role_prompt` → `developer_instructions`, `model` → `model` + `model_reasoning_effort`, `tools.*` → `sandbox_mode` (lossy at fine grain), `permission.edit` ↔ `sandbox_mode`. New IR field `nicknames` ↔ Codex-only `nickname_candidates`.

### Fixed

- Anti-pattern guidance flipped: treating Codex CLI as `AGENTS.md`-only is now explicitly called out as wrong; current Codex supports project-scoped TOML subagents.

## [0.2.5] - 2026-04-22

### Fixed

- **Codex CLI plugin discovery.** Marketplace plugin source path was bare `./`, which Codex's `resolve_local_plugin_source_path` rejects (the `./` prefix is stripped and an empty remainder is invalid). The plugin was silently dropped from `/plugin` even after `codex plugin marketplace add ytthuan/agents-system-setup` succeeded.
  - Source: openai/codex `codex-rs/core-plugins/src/marketplace.rs` (`resolve_local_plugin_source_path`, `MARKETPLACE_MANIFEST_RELATIVE_PATHS`) and `codex-rs/utils/plugins/src/plugin_namespace.rs` (`DISCOVERABLE_PLUGIN_MANIFEST_PATHS`).

### Changed

- **Repo layout.** Plugin payload moved from `skills/` (repo root) to `plugins/agents-system-setup/`, which now owns `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, and `skills/`. Both marketplace manifests (`.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`) now point at `./plugins/agents-system-setup`. Root `plugin.json` (Copilot) updated to `skills: ["plugins/agents-system-setup/skills/agents-system-setup"]`.
- Root `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` retained for direct local-path installs.
- Install scripts (`scripts/install-opencode.sh`, `scripts/install-opencode.ps1`) and docs (README, SECURITY) repathed.
- `scripts/_bump_version.py` now updates the new sub-tree manifests too — five files kept in sync.

### Added

- `scripts/_validate.py` gains a Codex-strict marketplace validator: rejects bare `./`, paths containing `..`, and paths whose target dir lacks a discoverable plugin manifest. Catches future regressions of this same class.

## [0.2.4] - 2026-04-22

### Added

- **Phase 8 — Final Wrap-Up** in `SKILL.md`: a single consolidated, multi-select prompt run after Phase 7 that surfaces a curated, source-cited menu of well-known add-ons (Spec-Kit, Anthropic/OpenAI evals, OpenTelemetry GenAI, OWASP LLM Top-10, Claude Code hooks, MCP security guidance, additional subagent catalogs, prompt versioning, cost/usage budgets).
- New reference `skills/agents-system-setup/references/wrapup.md` — full catalog with vendor-official source URLs, filter matrix gated by Phase 1.7 / 3 / 3.5 signals, and per-item action stubs.
- `.claude-plugin/marketplace.json` so Claude Code's marketplace browser recognizes the repo as a valid plugin source (was rejecting with "No plugins found... not a valid plugin marketplace").

### Changed

- Output Contract gains `Wrap-up add-ons selected/skipped` lines.
- Anti-patterns extended: skipping wrap-up, per-item round-robin instead of multi-select, citing unofficial sources in the wrap-up menu.

## [0.2.3] - 2026-04-22

### Added

- README badges: CI status, Release status, latest release version, MIT license, cross-OS, supported runtimes.

### Changed

- **GitHub Actions bumped to current majors** (via Dependabot PRs #1–#4):
  - `actions/checkout` v4 → v6
  - `actions/setup-python` v5 → v6
  - `softprops/action-gh-release` v2 → v3
  - `DavidAnson/markdownlint-cli2-action` v16 → v23 (ships markdownlint v0.40)
- Trimmed `SKILL.md` description from ~1.6 KB to 936 chars to satisfy the 1024-char skill-description limit.

### Fixed

- `.markdownlint.yaml`: disable MD051 (link-fragments) and MD060 (table-column-style) — new defaults in markdownlint v0.40 that produce only cosmetic noise.
- README Runtimes badge anchor: `#install` → `#install--per-runtime` to match the actual heading slug.

## [0.2.2] - 2026-04-22

### Added

- **Phase 1.7 — Domain Detection & Spec-Kit recommendation.** When the project brief matches a software-development keyword set or shows source-language signals, the skill now offers to install [GitHub Spec-Kit](https://github.com/github/spec-kit) for the chosen runtime (`copilot`, `claude`, `codex`, `opencode`).
- New reference doc `skills/agents-system-setup/references/spec-kit.md` covering positioning, install commands, and the `/specify` → `/plan` → `/tasks` → `/implement` workflow.
- New asset `skills/agents-system-setup/assets/spec-kit-block.snippet.md` — managed `AGENTS.md` block that documents the Spec-Driven workflow when Spec-Kit is opted in.
- Hard Rule #14: Spec-Kit recommendation is opt-in only and scoped to software-dev domains.

### Changed

- `assets/AGENTS.md.template` now has a `{{SPEC_KIT_BLOCK}}` placeholder rendered conditionally by Phase 4.
- `.markdownlint.yaml` disables MD012 so changelog stubs don't break the lint job.
- `scripts/_bump_version.py` tightens stub spacing to keep markdownlint green.

### Fixed

- CHANGELOG header had a stray blank line that tripped MD012 on CI.

## [0.2.1] - 2026-04-22

### Added

- Cross-OS CI matrix (Ubuntu / macOS / Windows) running validators, ShellCheck, PSScriptAnalyzer, and markdownlint on every push and PR.
- Tag-driven release workflow that publishes a tarball + SHA-256 to GitHub Releases when a `v*.*.*` tag is pushed.
- JSON Schemas for all four runtime manifests under `schemas/`.
- `scripts/validate.{sh,ps1}` — cross-platform validator (manifest schema, version sync across all four manifests, frontmatter checks, encoding, internal link resolution).
- `scripts/bump-version.{sh,ps1}` — atomic version bump across the four manifests + CHANGELOG stub generator.
- `.github/dependabot.yml` for weekly GitHub Actions updates.
- `SECURITY.md`, `CONTRIBUTING.md`, issue/PR templates, `.editorconfig`, `.markdownlint.yaml`.

### Changed

- Repository is now public so Actions runs on free-tier minutes.

### Fixed

- Validator now uses POSIX paths internally so dict lookups work on Windows.
- Validator output is ASCII + UTF-8 stdout to avoid Windows cp1252 `UnicodeEncodeError`.

## [0.2.0] — 2026-04-22

### Added
- **Native plugin manifests for Claude Code (`.claude-plugin/plugin.json`) and Codex CLI (`.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`)** — one-line install on both runtimes.
- **OpenCode install scripts** (`scripts/install-opencode.{sh,ps1}`) — clone-and-copy install for the runtime that doesn't support skill-bundle plugins natively.
- **Parallelism reference** (`skills/agents-system-setup/references/parallelism.md`) — defines parallel subagents vs Claude Code agent teams, parallel-safety derivation from Directory Architecture, wave-based execution, and per-runtime orchestrator prompt patterns.
- **Hard rule #13**: parallelism is mandatory where work is independent. Sequential-only topologies are an error.
- **Wave plan** in Phase 2 output and Agent Roster (`parallel-safe`, `wave` columns).
- **`AGENT-TEAMS.md` emission** for Claude Code projects when 3+ subagents are team-suitable.

### Changed
- Bumped version to 0.2.0.
- README rewritten with per-runtime install commands cross-referenced against vendor docs.

## [0.1.0] — 2026-04-22

Initial public release.

### Added
- Skill `agents-system-setup` with four modes: `init`, `update`, `improve`, `replicate`.
- Multi-runtime support: GitHub Copilot CLI, Claude Code, OpenCode, OpenAI Codex CLI.
- Canonical IR for bidirectional agent/skill/MCP replication across runtimes.
- Marketplace-first plugin/MCP discovery with vendor attribution.
- Mandatory MCP approval gate; per-item opt-in for all recommendations.
- Cross-OS scripts (`.sh` + `.ps1`) and `.gitattributes` for line-ending safety.
- DESIGN.md documenting reasoning behind every phase and hard rule.
