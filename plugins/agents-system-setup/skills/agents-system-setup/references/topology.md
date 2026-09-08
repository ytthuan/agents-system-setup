# Subagent Topology Guide

> **The orchestrator is the host CLI session reading `AGENTS.md`**, not a subagent file. `@orchestrator` is a routing alias for that host/root session (Copilot CLI / Claude Code / OpenCode / Codex / Gemini). No runtime emits a separate `orchestrator.agent.md`, `.claude/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.codex/agents/orchestrator.toml`, or `.gemini/agents/orchestrator.md`. Subagent files in the table below are for **specialized roles only**; orchestration responsibilities (planning, delegation, integration, approval gates) live in `AGENTS.md` › Orchestration Operating Model.

Subagent count scales with durable responsibilities and actual delegation
benefit. Zero specialists is valid when the host can satisfy all required
responsibilities and independence constraints; large systems may still justify
many specialists. The host orchestrator is always present and is not counted as
a subagent.

## Responsibility Catalog

These are logical responsibilities, not a mandatory process roster. Merge them
into the host or another role when scope is small and independence is not
required. Emit a specialist only when the concern is durable, discoverable,
and likely to benefit from separate context or permissions.

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
| `architecture-reviewer` | Preserve boundaries, ADRs, quality attributes, and design-pattern rationale; when `advisory_supervision` is on, also own the cross-session premise verdict | read-only + docs write if ADRs approved | `docs/adr/**`, architecture docs |
| `design-pattern-reviewer` | Check implementation against selected patterns and anti-patterns | read-only | *(none — read-only)* |

## Software-Development Build Gate Responsibilities

When the Build Gate is enabled, all required gates need explicit logical
owners. Reuse project roles or the host where independence is not required;
create a specialist only when its task benefits from isolation, repeatability,
or a restricted execution profile. Review must remain independent of the
writer.

| Subagent | Responsibility | Tool restrictions | Owned paths (Directory Architecture) |
|---|---|---|---|
| `build-runner` | Execute build commands; report status, artifact paths, log summary | read + execute build/formatter commands declared in plan | *(none — runs commands, may write build artifacts under generated dirs only)* |
| `change-bug-hunter` | Diff-scoped logic, regression, integration sniff + lightweight security check | read-only + bounded local search | *(none — read-only)* |
| `change-validator` | Aggregate gate evidence; emit final pre-merge integration report; enforce required approvals | read-only + aggregate | *(none — read-only; integrates evidence emitted by gate owners)* |

`change-validator` is a logical **evidence integration responsibility**, not a
correctness authority. Reviewer, tester, and security/architecture owners remain
authoritative on their gates. It may be performed by the host or merged into a
review role where permitted; it never overrides independent evidence.

`change-bug-hunter` and `vulnerability-researcher` follow the
mutual-exclusion routing rule documented in
[sdlc-build-gate.md](./sdlc-build-gate.md#mutual-exclusion-routing-change-bug-hunter-vs-vulnerability-researcher).
Do not duplicate scope.

## Per-Project-Type Candidate Responsibilities

These examples are menus, not required rosters. Start with the host, map
required responsibilities and gates, then emit only specialists that add
material value.

### Documentation site (mkdocs/docusaurus/astro)
Possible specialists: `content-writer`, `link-checker`, `style-reviewer`,
`build-runner`.

### Web — .NET
Possible specialists: `implementer`, `reviewer`, `tester`,
`security-auditor`, `architecture-reviewer`, `dotnet-build-runner`,
`ef-migrations`, `api-designer`; add `azure-deployer` only for Azure scope.

### Web — Node.js/TypeScript
Possible specialists: `implementer`, `reviewer`, `tester`,
`security-auditor`, `architecture-reviewer`, `frontend-ui`, `api-designer`,
`db-schema`, `playwright-e2e`; add framework roles only when relevant.

### Web — Python
Possible specialists: `implementer`, `reviewer`, `security-auditor`,
`architecture-reviewer`, `pytest-runner`, `api-designer`, `db-schema`,
`type-checker`.

### Web — Go
Possible specialists: `implementer`, `reviewer`, `security-auditor`,
`architecture-reviewer`, `go-test-runner`, `api-designer`,
`goroutine-auditor`.

### iOS
Possible specialists: `swiftui-implementer`, `appkit-interop`,
`xcode-build-runner`, `xctest-runner`, `signing-entitlements`,
`accessibility-auditor`; add `app-intents-designer` only for Shortcuts/Siri.

### Android
Possible specialists: `compose-implementer`, `gradle-runner`,
`instrumentation-tester`, `play-store-publisher`, `accessibility-auditor`.

### CLI tool
Possible specialists: `implementer`, `reviewer`, `tester`,
`security-auditor`, `architecture-reviewer`, `release-publisher`,
`man-page-writer`.

### Library / SDK
Possible specialists: `api-designer`, `implementer`, `reviewer`, `tester`,
`security-auditor`, `architecture-reviewer`, `semver-guardian`,
`docs-writer`, `release-publisher`.

### Monorepo
Possible specialists: selected package owners plus
`dependency-graph-analyst`, `affected-tests-runner`, `security-auditor`,
`architecture-reviewer`, `release-publisher`.

### Data / ML
Possible specialists: `notebook-runner`, `data-validator`, `model-trainer`,
`evaluator`, `pipeline-deployer`.

### Infrastructure / DevOps
Possible specialists: `terraform-planner`, `terraform-applier`,
`policy-checker`, `secret-scanner`, `cost-analyst`.

### Security team / Bug hunting
Possible specialists: `security-lead` (or host-owned lead),
`threat-modeler`, `vulnerability-researcher`, `validation-reproducer`,
`attack-path-analyst`, `remediation-verifier`. Add `bug-bounty-triage`,
`supply-chain-security`, `cloud-infra-security`, `incident-response-liaison`, or
`compliance-auditor` when the user requests disclosure, release/supply-chain,
cloud/infra, incident response, or compliance coverage. See
[security team](./security-team.md).

## Governance Sizing Rule

Security, audit, architecture, and design-pattern ownership is mandatory, but
ownership does not require a separate process. Responsibilities may be assigned
to the host or merged roles where independence is not required:

| Signal | Topology decision |
|---|---|
| Public/docs-only project, no code execution | Merge governance into `reviewer` and `docs-writer`; keep Security & Audit Matrix with `n/a` rationale where appropriate. |
| Any software project | Add `security-auditor` or explicitly merge its responsibilities into `reviewer`. Add `architecture-reviewer` or explicitly merge into `api-designer` / `reviewer`. |
| PII, payments, health, credentials, or regulated data | Dedicated `security-auditor`; consider `compliance-auditor`. |
| MCP servers, external APIs, or deploy/write tools | Add `threat-modeler` or merge that role into `security-auditor`; MCP approval gate remains mandatory. |
| Monorepo, microservices, event-driven, or cloud infrastructure | Dedicated `architecture-reviewer`; add `design-pattern-reviewer` when pattern consistency is a goal. |
| User asks for security team, bug hunting, vulnerability research, disclosure triage, or security analysis | Generate the dedicated security-team topology from [security team](./security-team.md); keep research roles read-mostly by default. |

## Requirements Triage Sizing Rule

Requirements triage is default-on as a **responsibility**. Use a separate
read-only worker only when ambiguity, scale, or risk makes isolated intake
valuable. Otherwise the host or planner performs it and records the merged
owner.

The triage agent never replaces the orchestrator. It returns an intake brief,
task classification, ambiguity list, `question_request` items, risk flags, and
recommended routing. The orchestrator owns user-facing questions, approval gates,
final plan decisions, and delegation.

## Content Quality Sizing Rule

Content-quality review is required when generated prose changes, but a separate
`agent-quality-curator` is optional. Use one when independent focused review
adds value; otherwise assign the responsibility to an independent reviewer or
the host when independence is not required.

The quality curator uses the signal taxonomy in
[content quality](./content-quality.md): `generic-description`,
`empty-rationale`, `padding-repetition`, `slop-completeness`,
`invented-attribution`, `context-bloat`, `vague-ownership`,
`unsupported-assertion`, `silent-gate-gap`, and `prompt-hygiene-risk`. It
reports `Content quality: ok|warn|fail|n/a; signals=<list|none>` and never
replaces reviewer, tester, security, architecture, or validator roles.

## Code Quality Sizing Rule

Code-quality review is default-on for software-dev projects (it rides the Phase
1.7 classification, like the Build Gate). The logical owner covers maintainability,
project-convention-conformance, and code-smell verdict for source-code changes —
distinct from `@reviewer` (correctness), `architecture-reviewer` (boundaries),
and `change-bug-hunter` (diff-scoped bugs). It is **read-only** and never
substitutes for the Build Gate.

| Signal | Topology decision |
|---|---|
| `code_quality_strictness` is `standard` or `strict` | Assign an independent read-only reviewer; use a separate `code-quality-reviewer` only when it adds value. |
| `code_quality_strictness` is `light` or `advisory`, or a tiny direct setup | Merge the responsibility into `@reviewer` and record `code_quality_reviewer = merged`. |
| `code_quality_strictness` is `skipped` or `n/a` (non-software / no source code) | Do not emit the role; render the `n/a` rationale in `AGENTS.md`. |

The implementer (and other edit-capable roles) apply the standards from
[code-quality](./code-quality.md) **while writing**; the reviewer confirms them.
All edit-capable and reviewer roles emit `Code quality: ok|warn|fail|n/a;
signals=<list|none>`, which `@change-validator` folds into the Build Gate review
evidence. Do not confuse `code-quality` (project source) with `content-quality`
(generated agent prose).

## Advisory Supervision Routing

`advisory_supervision` (see [parallelism](./parallelism.md#supervising-a-running-child-session))
adds **no new role**. The premise verdict on a running child session goes to the
existing `architecture-reviewer`, which receives a host-composed premise packet
and returns `Advisory verdict` / `premise` / `note`. Rationale: the only field
that is not already owned — `premise` — requires visibility across every sibling
unit, and only the host session has that. A dedicated advisor subagent would need
the host to pre-assemble the comparison it exists to perform.

| Signal | Topology decision |
|---|---|
| `advisory_supervision` is `plan-gate` or `standard` | `architecture-reviewer` also owns the cross-session premise verdict. |
| `architecture-reviewer` is merged into `@reviewer` / `api-designer` (tiny setup) | The merged role carries the verdict; record `advisory_verdict_owner = merged`. |
| `advisory_supervision` is `off` or the user did not opt in | Do not mention it in the roster. |

The verdict owner is **read-only** and never calls `respond_to_session_plan` or
`send_session_message` — subagents never orchestrate sessions (hard rule #33/#36).
Only the host acts on the verdict.

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

> At most one subagent per **durable concern**. One-shot procedures are skills,
> not subagents; host-owned responsibilities need no agent file.

If the user requests 50, support it — generate one agent file per concern they list.

## Directory Architecture Generation

For every chosen subagent, derive a row in AGENTS.md › Directory Architecture:

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| (from subagent's "Owned paths") | (subagent's responsibility) | `@<subagent-name>` | `owned` (or `additive-only` for docs/tests) |

Add applicable control rows regardless of specialist count. `@orchestrator` is
the host CLI session reading `AGENTS.md`; other owner labels may name a
specialist or a logical responsibility merged into the host/reviewer.

| Path glob | Purpose | Owner | Edit rule |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | Agent project memory (host orchestrator + pointer files) | `@orchestrator` (host session) | `owned` |
| `{{PROJECT_POLICY_PATH}}` (normally `docs/agents/project-policy.md`) | Full human-input, governance, capability, review/triage, and instruction-memory policy | `@orchestrator` + applicable governance owners | `owned` |
| `.github/agents/**`, `.claude/agents/**`, `.opencode/agents/**`, `.codex/agents/**`, `.gemini/agents/**` | Specialized subagent definitions (never an orchestrator file) | `@orchestrator` (host session) | `owned` |
| `.github/skills/**`, `.claude/skills/**`, `.opencode/skills/**`, `.agents/skills/**`, `.gemini/skills/**` | Skill packages | `@orchestrator` (host session) | `additive-only` |
| `.mcp.json`, `opencode.json` | MCP / runtime config (incl. OpenCode root-session `permission.task` gate) | `@orchestrator` (host session) | `owned` (gated by approval) |
| `.env*`, secret/config files | Secrets and local config | `@security-auditor` | `read-only` |
| `docs/security/**`, `security-reports/**` | Security team findings, threat models, and approved audit artifacts | `@security-lead` / `@security-auditor` | `additive-only` unless the plan grants update ownership |
| CI/release config (`.github/workflows/**`, release scripts) | Supply-chain and release controls | `@release-publisher` + `@security-auditor` | `shared` |
| Dependency manifests / lockfiles | Dependency inventory and supply-chain review | `@security-auditor` + language owner | `shared` |
| `docs/adr/**`, architecture docs | Architecture decisions and design rationale | `@architecture-reviewer` | `additive-only` |
| `plan.md`, `**/plan.md` | Active task plans | `@planner` | `owned` |
| Generated dirs (`dist/`, `build/`, `target/`, `bin/`, `obj/`) | Build output | *(none)* | `read-only` |
