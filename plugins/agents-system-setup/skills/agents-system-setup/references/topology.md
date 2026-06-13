# Subagent Topology Guide

> **The orchestrator is the host CLI session reading `AGENTS.md`**, not a subagent file. `@orchestrator` is a routing alias for that host/root session (Copilot CLI / Claude Code / OpenCode / Codex / Gemini). No runtime emits a separate `orchestrator.agent.md`, `.claude/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.codex/agents/orchestrator.toml`, or `.gemini/agents/orchestrator.md`. Subagent files in the table below are for **specialized roles only**; orchestration responsibilities (planning, delegation, integration, approval gates) live in `AGENTS.md` › Orchestration Operating Model.

Subagent count scales with project scope (3 minimum, no fixed maximum — small projects ~3, large monorepos may legitimately need 20+). The host orchestrator is always present (it is the host session); subagent file counts do not include it.

## Universal Subagents (consider for every project)

Each row also names the **owned paths** that feed into AGENTS.md › Directory Architecture.

| Subagent | Responsibility | Tool restrictions | Owned paths (Directory Architecture) |
|---|---|---|---|
| `requirements-triage` | Analyze the user's request, classify task type/risk, find ambiguity, propose first questions, and recommend routing before planning | read-only + `question_request` to orchestrator | *(none — read-only; may draft a plan seed in the orchestrator's plan)* |
| `agent-quality-curator` | Review generated agent, skill, memory, recommendation, and output-contract prose for specificity, grounding, evidence, prompt hygiene, and context bloat | read-only + content-quality signals; no final approval ownership | *(none — read-only; may propose concise fixes to orchestrator)* |
| `planner` | Decompose tasks, write plan.md | read-only + write to plan.md | `plan.md`, `**/plan.md` |
| `implementer` | Make code changes | full file edit + bash | source dirs (project-specific) |
| `reviewer` | Critique diffs, flag risks | read-only + bash (lint/test) | *(none — read-only)* |
| `code-quality-reviewer` | Maintainability, project-convention conformance, and code-smell verdict for source-code changes (software-dev) | read-only + bash (lint/format check) | *(none — read-only; merges into `@reviewer` for light/advisory/tiny)* |
| `tester` | Run/extend tests, triage failures | read + bash | `tests/**`, `**/__tests__/**`, `**/*.test.*`, `**/*.spec.*` |
| `docs-writer` | Update README/CHANGELOG/docs | docs files only | `README.md`, `CHANGELOG.md`, `docs/**`, `**/*.md` (excluding agent files) |
| `security-auditor` | Review secrets, tool/MCP boundaries, dependency risk, least privilege | read-only + bash for scanners/tests | *(none by default — read-only; tightly scoped remediation only if approved)* |
| `threat-modeler` | Map assets, trust boundaries, attacker stories, and security invariants | read-only | *(none — read-only)* |
| `vulnerability-researcher` | Discover plausible source/control/sink security candidates in authorized scope | read-only + bounded local search | *(none — read-only)* |
| `validation-reproducer` | Confirm, falsify, or defer candidate findings with bounded evidence | read-only by default; runner only after approval | validation artifacts under approved output path |
| `attack-path-analyst` | Establish reachability, counterevidence, severity, priority, and proof gaps | read-only | *(none — read-only)* |
| `remediation-verifier` | Verify fixes, regression tests, and nearby bypass variants | read-only unless routed through owning implementer | tests/verification artifacts when approved |
| `architecture-reviewer` | Preserve boundaries, ADRs, quality attributes, and design-pattern rationale | read-only + docs write if ADRs approved | `docs/adr/**`, architecture docs |
| `design-pattern-reviewer` | Check implementation against selected patterns and anti-patterns | read-only | *(none — read-only)* |

## Software-Dev Universal Subagents (Build Gate)

These three roles are added when Phase 1.7 classifies the project as
`software-dev` AND Q9d Build Gate strictness is not `Skip`. They follow the
SDLC quality bar from [SDLC build gate](./sdlc-build-gate.md).

| Subagent | Responsibility | Tool restrictions | Owned paths (Directory Architecture) |
|---|---|---|---|
| `build-runner` | Execute build commands; report status, artifact paths, log summary | read + execute build/formatter commands declared in plan | *(none — runs commands, may write build artifacts under generated dirs only)* |
| `change-bug-hunter` | Diff-scoped logic, regression, integration sniff + lightweight security check | read-only + bounded local search | *(none — read-only)* |
| `change-validator` | Aggregate gate evidence; emit final pre-merge integration report; enforce required approvals | read-only + aggregate | *(none — read-only; integrates evidence emitted by gate owners)* |

`change-validator` is an **evidence integrator**, not a correctness
authority. `@reviewer`, `@tester`, and security/architecture owners remain
authoritative on their gates. When Q9d strictness is `Light`,
`change-validator` merges into `@reviewer` and is not emitted as a separate
subagent.

`change-bug-hunter` and `vulnerability-researcher` follow the
mutual-exclusion routing rule documented in
[sdlc-build-gate.md](./sdlc-build-gate.md#mutual-exclusion-routing-change-bug-hunter-vs-vulnerability-researcher).
Do not duplicate scope.

## Per-Project-Type Recommendations

### Documentation site (mkdocs/docusaurus/astro)
Orchestrator + `content-writer`, `link-checker`, `style-reviewer`, `build-runner`.

### Web — .NET
Orchestrator + `planner`, `implementer`, `reviewer`, `tester`, `security-auditor`, `architecture-reviewer`, `dotnet-build-runner`, `ef-migrations`, `api-designer`. Add `azure-deployer` if Azure.

### Web — Node.js/TypeScript
Orchestrator + `planner`, `implementer`, `reviewer`, `tester`, `security-auditor`, `architecture-reviewer`, `frontend-ui`, `api-designer`, `db-schema`, `playwright-e2e`. Add `next-app-router-expert` if Next.js.

### Web — Python
Orchestrator + `planner`, `implementer`, `reviewer`, `security-auditor`, `architecture-reviewer`, `pytest-runner`, `api-designer`, `db-schema`, `type-checker` (mypy/pyright).

### Web — Go
Orchestrator + `planner`, `implementer`, `reviewer`, `security-auditor`, `architecture-reviewer`, `go-test-runner`, `api-designer`, `goroutine-auditor`.

### iOS
Orchestrator + `swiftui-implementer`, `appkit-interop`, `xcode-build-runner`, `xctest-runner`, `signing-entitlements`, `accessibility-auditor`. Add `app-intents-designer` if Shortcuts/Siri scope.

### Android
Orchestrator + `compose-implementer`, `gradle-runner`, `instrumentation-tester`, `play-store-publisher`, `accessibility-auditor`.

### CLI tool
Orchestrator + `implementer`, `reviewer`, `tester`, `security-auditor`, `architecture-reviewer`, `release-publisher`, `man-page-writer`.

### Library / SDK
Orchestrator + `api-designer`, `implementer`, `reviewer`, `tester`, `security-auditor`, `architecture-reviewer`, `semver-guardian`, `docs-writer`, `release-publisher`.

### Monorepo
Orchestrator + per-package subagents derived from workspace members + `dependency-graph-analyst`, `affected-tests-runner`, `security-auditor`, `architecture-reviewer`, `release-publisher`.

### Data / ML
Orchestrator + `notebook-runner`, `data-validator`, `model-trainer`, `evaluator`, `pipeline-deployer`.

### Infrastructure / DevOps
Orchestrator + `terraform-planner`, `terraform-applier`, `policy-checker`, `secret-scanner`, `cost-analyst`.

### Security team / Bug hunting
Orchestrator + `security-lead` (or orchestrator-owned lead in compact setups),
`threat-modeler`, `vulnerability-researcher`, `validation-reproducer`,
`attack-path-analyst`, `remediation-verifier`. Add `bug-bounty-triage`,
`supply-chain-security`, `cloud-infra-security`, `incident-response-liaison`, or
`compliance-auditor` when the user requests disclosure, release/supply-chain,
cloud/infra, incident response, or compliance coverage. See
[security team](./security-team.md).

## Governance Sizing Rule

Security, audit, architecture, and design-pattern ownership is mandatory, but roles may be merged for small repositories:

| Signal | Topology decision |
|---|---|
| Public/docs-only project, no code execution | Merge governance into `reviewer` and `docs-writer`; keep Security & Audit Matrix with `n/a` rationale where appropriate. |
| Any software project | Add `security-auditor` or explicitly merge its responsibilities into `reviewer`. Add `architecture-reviewer` or explicitly merge into `api-designer` / `reviewer`. |
| PII, payments, health, credentials, or regulated data | Dedicated `security-auditor`; consider `compliance-auditor`. |
| MCP servers, external APIs, or deploy/write tools | Add `threat-modeler` or merge that role into `security-auditor`; MCP approval gate remains mandatory. |
| Monorepo, microservices, event-driven, or cloud infrastructure | Dedicated `architecture-reviewer`; add `design-pattern-reviewer` when pattern consistency is a goal. |
| User asks for security team, bug hunting, vulnerability research, disclosure triage, or security analysis | Generate the dedicated security-team topology from [security team](./security-team.md); keep research roles read-mostly by default. |

## Requirements Triage Sizing Rule

`requirements-triage` is **default-on recommended**. Generate it as a separate
subagent for normal, ambiguous, cross-runtime, security-sensitive, release, MCP,
replication, or multi-wave setups. For tiny direct setups, merge the
responsibility into `planner` and record `requirements_triage_status = merged`.

The triage agent never replaces the orchestrator. It returns an intake brief,
task classification, ambiguity list, `question_request` items, risk flags, and
recommended routing. The orchestrator owns user-facing questions, approval gates,
final plan decisions, and delegation.

## Content Quality Sizing Rule

`agent-quality-curator` is **universal recommended** for generated agent systems.
Generate it as a separate read-only subagent for normal, complex, cross-runtime,
audit, improve, replication, MCP, release, skill-heavy, or multi-wave setups.
For tiny direct setups, merge the responsibility into `reviewer` and record
`content_quality_curator = merged`. Skip only with explicit rationale.

The quality curator uses the signal taxonomy in
[content quality](./content-quality.md): `generic-description`,
`empty-rationale`, `padding-repetition`, `slop-completeness`,
`invented-attribution`, `context-bloat`, `vague-ownership`,
`unsupported-assertion`, `silent-gate-gap`, and `prompt-hygiene-risk`. It
reports `Content quality: ok|warn|fail|n/a; signals=<list|none>` and never
replaces reviewer, tester, security, architecture, or validator roles.

## Code Quality Sizing Rule

`code-quality-reviewer` is **default-on for software-dev projects** (it rides the
Phase 1.7 classification, like the Build Gate). It owns the maintainability,
project-convention-conformance, and code-smell verdict for source-code changes —
distinct from `@reviewer` (correctness), `architecture-reviewer` (boundaries),
and `change-bug-hunter` (diff-scoped bugs). It is **read-only** and never
substitutes for the Build Gate.

| Signal | Topology decision |
|---|---|
| `code_quality_strictness` is `standard` or `strict` | Generate `code-quality-reviewer` as a separate read-only subagent. |
| `code_quality_strictness` is `light` or `advisory`, or a tiny direct setup | Merge the responsibility into `@reviewer` and record `code_quality_reviewer = merged`. |
| `code_quality_strictness` is `skipped` or `n/a` (non-software / no source code) | Do not emit the role; render the `n/a` rationale in `AGENTS.md`. |

The implementer (and other edit-capable roles) apply the standards from
[code-quality](./code-quality.md) **while writing**; the reviewer confirms them.
All edit-capable and reviewer roles emit `Code quality: ok|warn|fail|n/a;
signals=<list|none>`, which `@change-validator` folds into the Build Gate review
evidence. Do not confuse `code-quality` (project source) with `content-quality`
(generated agent prose).

## Security Team Sizing Rule

Dedicated security-team generation is opt-in or risk-triggered; it is not the
default for every software project.

| Signal | Security-team decision |
|---|---|
| Routine software project | Keep `security-auditor` or merged reviewer security responsibility. |
| User selects `Security team / Bug hunting` or asks for bug hunting/security analysis | Generate the dedicated team: `security-lead` or orchestrator-owned lead, `threat-modeler`, `vulnerability-researcher`, `validation-reproducer`, `attack-path-analyst`, and `remediation-verifier`. |
| External reports, disclosure, bounty, or coordinated vulnerability handling | Add `bug-bounty-triage` with read-only communication/triage duties. |
| Release, dependency, package, CI, or artifact trust is in scope | Add `supply-chain-security` or route supply-chain duties through `security-auditor`. |
| Cloud, IaC, Kubernetes, network exposure, or secrets boundary is in scope | Add `cloud-infra-security` or merge into infra/security owner. |
| Confirmed high-impact issue may need containment or comms | Add `incident-response-liaison`; it records escalation paths but does not disclose publicly. |
| Compliance evidence is required | Add `compliance-auditor` with read-only evidence mapping. |

Security discovery, validation, attack-path, triage, and compliance agents are
read-mostly by default. Remediation writes route through the owning implementer
unless the plan explicitly grants narrow owned paths and approvals.

## Sizing Rule

> One subagent per **durable concern** (lasts beyond a single task). One-shot procedures are **skills**, not subagents.

If the user requests 50, support it — generate one agent file per concern they list.

## Directory Architecture Generation

For every chosen subagent, derive a row in AGENTS.md › Directory Architecture:

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| (from subagent's "Owned paths") | (subagent's responsibility) | `@<subagent-name>` | `owned` (or `additive-only` for docs/tests) |

Add **always-present** rows regardless of project type. `@orchestrator` is the host CLI session reading `AGENTS.md` (no subagent file emitted); the remaining owners are real subagents.

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | Agent project memory (host orchestrator + pointer files) | `@orchestrator` (host session) | `owned` |
| `.github/agents/**`, `.claude/agents/**`, `.opencode/agents/**`, `.codex/agents/**`, `.gemini/agents/**` | Specialized subagent definitions (never an orchestrator file) | `@orchestrator` (host session) | `owned` |
| `.github/skills/**`, `.claude/skills/**`, `.opencode/skills/**`, `.gemini/skills/**` | Skill packages | `@orchestrator` (host session) | `additive-only` |
| `.mcp.json`, `opencode.json` | MCP / runtime config (incl. OpenCode root-session `permission.task` gate) | `@orchestrator` (host session) | `owned` (gated by approval) |
| `.env*`, secret/config files | Secrets and local config | `@security-auditor` | `read-only` |
| `docs/security/**`, `security-reports/**` | Security team findings, threat models, and approved audit artifacts | `@security-lead` / `@security-auditor` | `additive-only` unless the plan grants update ownership |
| CI/release config (`.github/workflows/**`, release scripts) | Supply-chain and release controls | `@release-publisher` + `@security-auditor` | `shared` |
| Dependency manifests / lockfiles | Dependency inventory and supply-chain review | `@security-auditor` + language owner | `shared` |
| `docs/adr/**`, architecture docs | Architecture decisions and design rationale | `@architecture-reviewer` | `additive-only` |
| `plan.md`, `**/plan.md` | Active task plans | `@planner` | `owned` |
| Generated dirs (`dist/`, `build/`, `target/`, `bin/`, `obj/`) | Build output | *(none)* | `read-only` |
