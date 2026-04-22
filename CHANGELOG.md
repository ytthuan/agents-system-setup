# Changelog

All notable changes to this plugin are documented here. Format: [Keep a Changelog](https://keepachangelog.com).

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
