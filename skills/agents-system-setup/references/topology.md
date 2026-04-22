# Subagent Topology Guide

The orchestrator is **always** present. Subagent count scales with project scope (3 minimum, no fixed maximum — small projects ~3, large monorepos may legitimately need 20+).

## Universal Subagents (consider for every project)

Each row also names the **owned paths** that feed into AGENTS.md › Directory Architecture.

| Subagent | Responsibility | Tool restrictions | Owned paths (Directory Architecture) |
|---|---|---|---|
| `planner` | Decompose tasks, write plan.md | read-only + write to plan.md | `plan.md`, `**/plan.md` |
| `implementer` | Make code changes | full file edit + bash | source dirs (project-specific) |
| `reviewer` | Critique diffs, flag risks | read-only + bash (lint/test) | *(none — read-only)* |
| `tester` | Run/extend tests, triage failures | read + bash | `tests/**`, `**/__tests__/**`, `**/*.test.*`, `**/*.spec.*` |
| `docs-writer` | Update README/CHANGELOG/docs | docs files only | `README.md`, `CHANGELOG.md`, `docs/**`, `**/*.md` (excluding agent files) |

## Per-Project-Type Recommendations

### Documentation site (mkdocs/docusaurus/astro)
Orchestrator + `content-writer`, `link-checker`, `style-reviewer`, `build-runner`.

### Web — .NET
Orchestrator + `planner`, `implementer`, `reviewer`, `tester`, `dotnet-build-runner`, `ef-migrations`, `api-designer`. Add `azure-deployer` if Azure.

### Web — Node.js/TypeScript
Orchestrator + `planner`, `implementer`, `reviewer`, `tester`, `frontend-ui`, `api-designer`, `db-schema`, `playwright-e2e`. Add `next-app-router-expert` if Next.js.

### Web — Python
Orchestrator + `planner`, `implementer`, `reviewer`, `pytest-runner`, `api-designer`, `db-schema`, `type-checker` (mypy/pyright).

### Web — Go
Orchestrator + `planner`, `implementer`, `reviewer`, `go-test-runner`, `api-designer`, `goroutine-auditor`.

### iOS
Orchestrator + `swiftui-implementer`, `appkit-interop`, `xcode-build-runner`, `xctest-runner`, `signing-entitlements`, `accessibility-auditor`. Add `app-intents-designer` if Shortcuts/Siri scope.

### Android
Orchestrator + `compose-implementer`, `gradle-runner`, `instrumentation-tester`, `play-store-publisher`, `accessibility-auditor`.

### CLI tool
Orchestrator + `implementer`, `reviewer`, `tester`, `release-publisher`, `man-page-writer`.

### Library / SDK
Orchestrator + `api-designer`, `implementer`, `reviewer`, `tester`, `semver-guardian`, `docs-writer`, `release-publisher`.

### Monorepo
Orchestrator + per-package subagents derived from workspace members + `dependency-graph-analyst`, `affected-tests-runner`, `release-publisher`.

### Data / ML
Orchestrator + `notebook-runner`, `data-validator`, `model-trainer`, `evaluator`, `pipeline-deployer`.

### Infrastructure / DevOps
Orchestrator + `terraform-planner`, `terraform-applier`, `policy-checker`, `secret-scanner`, `cost-analyst`.

## Sizing Rule

> One subagent per **durable concern** (lasts beyond a single task). One-shot procedures are **skills**, not subagents.

If the user requests 50, support it — generate one agent file per concern they list.

## Directory Architecture Generation

For every chosen subagent, derive a row in AGENTS.md › Directory Architecture:

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| (from subagent's "Owned paths") | (subagent's responsibility) | `@<subagent-name>` | `owned` (or `additive-only` for docs/tests) |

Add **always-present** rows regardless of project type:

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md` | Agent project memory | `@orchestrator` | `owned` |
| `.github/agents/**`, `.claude/agents/**`, `.opencode/agents/**` | Agent definitions | `@orchestrator` | `owned` |
| `.github/skills/**`, `.claude/skills/**`, `.opencode/skills/**` | Skill packages | `@orchestrator` | `additive-only` |
| `.mcp.json`, `opencode.json` | MCP / runtime config | `@orchestrator` | `owned` (gated by approval) |
| `plan.md`, `**/plan.md` | Active task plans | `@planner` | `owned` |
| Generated dirs (`dist/`, `build/`, `target/`, `bin/`, `obj/`) | Build output | *(none)* | `read-only` |
