# Changelog

All notable changes to this plugin are documented here. Format: [Keep a Changelog](https://keepachangelog.com).


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
