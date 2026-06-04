# SDLC Build Gate

Use this reference when the plugin generates an agent system for a
software-development project (web, app, CLI, library, monorepo, IaC). The
Build Gate ensures every code change passes a diff-aware quality bar before
being declared done: build, unit test, e2e test, code review, change-scoped
bug hunt, and final validation.

This reference is source-backed and original. Do not copy text or workflow
schemas from proprietary CI/CD products.

## Source-backed model

| Source | Public concept used here |
|---|---|
| DORA / Accelerate (Forsgren, Humble, Kim) | Continuous delivery quality gates: trunk-based development, fast feedback, every change is build-/test-verified before merge. |
| Google Engineering Practices (eng-practices public docs) | Small CLs, scope-aware code review, reviewer responsibility, sign-off discipline. |
| Trunk-Based Development (paulhammant.com) | Short-lived branches, pre-merge gate, build/test/lint as required signals. |
| OpenSSF SLSA v1.0 | Build provenance, isolated builds, evidence chain for release artifacts. |
| OWASP ASVS L1/L2 verification | Verification levels mapped to change risk; higher risk surfaces require deeper checks. |
| NIST SSDF SP 800-218 (PW.7, PW.8, PW.9, RV.1) | Reviewing software design + code, testing executable code, integrity verification, vulnerability identification. |
| Microsoft 1ES public guidance | Required reviewers, branch policies, evidence retention before merge. |

## When to generate the Build Gate

Generate the Build Gate when **all** of these are true:

- Phase 1.7 classified the project as `software-dev`.
- The Phase 0 mode is `init`, `update`, `improve`, or `upgrade` (not pure
  replicate).
- The user did not pick `Skip` for the Build Gate question (Q9d).

For non-software-dev projects (documentation site, security-team-only,
research), render `Build Gate (SDLC): n/a — non-software project` in the
AGENTS.md placeholder and skip role/skill emission.

## Diff bucket model

A change's bucket is the **maximum of `size_bucket` and `criticality_bucket`**
(`max(size_bucket, criticality_bucket)`). Size never overrides criticality.
A one-line change to auth middleware is L or XL, never XS.

### Size bucket

| Bucket | Files changed | Lines changed (sum of additions + deletions) |
|---|---|---|
| XS | 1 | ≤ 10 |
| S | ≤ 3 | ≤ 50 |
| M | ≤ 10 | ≤ 200 |
| L | ≤ 25 | ≤ 500 |
| XL | > 25 or no upper bound | > 500 |

Whitespace-only, generated-file-only, and lockfile-bump-only changes drop one
bucket (but never below XS).

### Criticality bucket

A change touches any of these surfaces → minimum bucket is **L** unless noted:

| Surface | Examples | Minimum bucket |
|---|---|---|
| Auth / authz / session middleware | login, sign-in, token issuance, RBAC | L |
| Crypto / signing / token handling | JWT signing keys, KMS, hashing | L |
| Public API / exported symbols / ABI | public `index.ts`, `pub fn`, OpenAPI surface | L |
| Schema / migration / database model | `schema.sql`, ORM models, ALTER scripts | L |
| Dependency manifest / lockfile | `package.json`, `requirements.txt`, `Cargo.lock` | M |
| Feature flag / config default | flag rollout, default-on, env defaults | M |
| Serialization / deserialization | wire format, protobuf, marshalers | M |
| Permission / policy / IaC | Terraform, Bicep, Kubernetes RBAC, IAM | L |
| Billing / payments / privacy / telemetry | invoicing, PII collection, consent | L |
| CI / release / signing / provenance | release workflows, signing scripts | L |
| Auth-adjacent middleware | rate limiting, CSRF, CORS | M |
| Recovery / backup / data retention | retention scripts, deletion paths | L |

If two or more `M`-surface markers fire together, escalate to `L`. If any `L`
fires together with another `L` or with security-team scope, escalate to `XL`.

## Gate matrix

Each bucket maps to a required gate set. The Build Gate is **fail-closed**:
missing evidence for a required gate blocks change-validator sign-off.

| Bucket | Build | Unit test | E2E test | Code review | Change bug hunt | Validation | Notes |
|---|---|---|---|---|---|---|---|
| XS | ✅ | 🟡 (smoke if applicable) | n/a | ✅ (single approver OK) | n/a | ✅ (fast lane) | docs-only, lockfile bump, whitespace, comment-only |
| S | ✅ | ✅ | 🟡 (affected paths only) | ✅ | 🟡 (diff scan) | ✅ | typical small refactor |
| M | ✅ | ✅ | ✅ (affected paths) | ✅ (review of public-surface impact) | ✅ | ✅ | normal feature work |
| L | ✅ | ✅ | ✅ (full suite for affected modules) | ✅ (≥ 2 reviewers when supported; security owner reviews if security/L) | ✅ (focused security + regression) | ✅ (architecture review when boundaries touched) | feature with shared boundary or critical surface |
| XL | ✅ | ✅ | ✅ (full suite) | ✅ (architecture + security owner mandatory) | ✅ (deep hunt; security team if dedicated) | ✅ (formal change-validator sign-off; release/CI hooks verified) | release-shaped change, multi-module refactor, schema migration |

`🟡` = recommended; runs by default but may be waived with explicit rationale
recorded in the plan. `n/a` = not required by the bucket; runs only if the
host orchestrator chooses to.

## Evidence schema

Each required gate produces evidence in the change-validator integration
report. Subagents emit evidence in their Reporting Template; change-validator
aggregates.

| Gate | Owner | Evidence shape |
|---|---|---|
| Build | `@build-runner` | command, exit status, build artifact paths, log summary |
| Unit test | `@tester` (or language-specific runner) | command, pass/fail counts, coverage delta if available, failing test names |
| E2E test | `@playwright-e2e` or runtime equivalent | command, scenarios run, pass/fail, screenshots/traces stored path |
| Code review | `@reviewer` | reviewed file paths, signed-off-by, blocking comments resolved (or rationale waived) |
| Change bug hunt | `@change-bug-hunter` | scanned paths, candidate count, suspicion list, severity, link to evidence |
| Validation | `@change-validator` | aggregated gate status, required-approval status, residual risk note |

## Strictness

User picks one in Q9d:

| Strictness | Behavior |
|---|---|
| Standard (default) | Use the matrix as written. `🟡` gates can be waived with rationale. |
| Strict | Promote all `🟡` to `✅`. XL requires two reviewer approvals and a release-validator sign-off. |
| Light | `change-validator` merges into `@reviewer`; XS keeps only build + review; M demotes e2e to `🟡`. Suitable for small teams or library code with thin runtime. |
| Skip | Do not generate Build Gate roles, snippet, or skill. Render `n/a — user skipped` in AGENTS.md. |

## Roles

The Build Gate adds at most three new universal-conditional subagents:

| Role | Read/Write | Owns | Boundary |
|---|---|---|---|
| `build-runner` | read + execute build commands | build invocation, build-output evidence | does not change source; may run formatters listed in plan |
| `change-bug-hunter` | read-only + bounded local search | diff-scoped logic, regression, integration sniff + lightweight security check | does not duplicate `vulnerability-researcher`; if a dedicated security team exists, only flags suspicions and hands findings to `vulnerability-researcher` |
| `change-validator` | read-only + aggregate | final pre-merge integration report | is an **evidence integrator**, not a correctness authority; reviewer/tester/security owners remain authoritative on their gates; merges into `@reviewer` when strictness = `Light` |

If the project already has roles that cover a gate, reuse them:

- `tester` / `pytest-runner` / `go-test-runner` / `xctest-runner` etc. → unit test gate.
- `playwright-e2e` (or runtime equivalent) → e2e gate; add only if not present.
- `reviewer` → code-review gate.
- `security-auditor` / `vulnerability-researcher` (when present) → upgrade routing rule below.

## Mutual-exclusion routing: `change-bug-hunter` vs `vulnerability-researcher`

Both are read-only and could overlap. Apply this rule in the generated
AGENTS.md › Routing section:

| Scenario | Route to |
|---|---|
| Diff-scoped regression, logic bug, integration glitch, lightweight security sniff | `change-bug-hunter` |
| Program/repo-scoped threat-driven source-control-sink research | `vulnerability-researcher` |
| Both roles exist + security suspicion arises on a diff | `change-bug-hunter` records the suspicion + summary; `vulnerability-researcher` owns the deeper threat analysis |
| Bug-bounty / disclosure / coordinated triage | `bug-bounty-triage` or `security-lead` (per security team) |

`change-bug-hunter` never escalates to remediation writes; remediation routes
through the owning implementer per the architecture/security ownership rules.

## Wave assignment

The Build Gate respects the existing wave/parallelism rules:

- `build-runner` and `tester` are parallel-safe in the same wave when build
  output is not a dependency of tests (most language toolchains build before
  test as a single step; emit them sequentially in those cases).
- `change-bug-hunter`, `reviewer`, and `playwright-e2e` are parallel-safe with
  each other once the build/unit tests pass; place them in the same wave.
- `change-validator` always runs last in its own wave; it waits for every
  preceding gate before emitting the integration report.

## AGENTS.md placement

The plugin renders the Build Gate in two places:

1. **`AGENTS.md` › `## Build Gate (SDLC)`** — compact mandatory inline
   checklist with the matrix snippet. This is the **fail-closed enforcement
   surface**: the host orchestrator runs the gate even if the skill is never
   invoked. The compact form lists bucket → required gates → evidence and
   tells the host to delegate per the routing table.
2. **`code-change-build-gate` skill** (per runtime, including Codex) — the
   expanded procedure: how to compute the bucket, criticality markers, how
   to gather evidence per gate, escalation paths, anti-patterns. Loaded on
   demand when the host needs depth.

## Anti-patterns

- Treating size buckets as the only signal — criticality always wins.
- Letting `change-validator` override reviewer/tester correctness verdicts.
- Letting `change-bug-hunter` duplicate full threat-model analysis when a
  security team is present.
- Adding the Build Gate to documentation-only or security-team-only projects.
- Generating Build Gate roles without the AGENTS.md inline checklist (silent
  skill = silent gate).
- Pinning concrete LOC counts inside generated AGENTS.md — use bucket labels
  and link to this reference.
- **Routing required Build Gate evidence through native task-class built-ins** (Copilot `task`, Claude `general-purpose`, OpenCode `general`). Build, unit test, e2e, code review, change bug hunt, and validation evidence MUST be owned by `@build-runner` / `@tester` / `@playwright-e2e` / `@reviewer` / `@change-bug-hunter` / `@change-validator`. Native task-class output is `non-gate evidence` — usable for ad-hoc orchestrator checks only. See [host-builtins-routing](./host-builtins-routing.md).

## Verification

After generation, the plugin verifier confirms:

1. `AGENTS.md` contains `## Build Gate (SDLC)` with a non-empty matrix or
   an `n/a — non-software project | user skipped` rationale.
2. For software-dev + not-skipped: `code-change-build-gate` skill exists at
   each selected runtime's skills path (including Codex).
3. Roster includes `build-runner`, `change-bug-hunter`, and
   `change-validator` (or `change-validator merged into reviewer` for
   `Light`).
4. Wave plan places `change-validator` last with `waits_for` covering every
   preceding gate.
5. Routing table contains the `change-bug-hunter` vs `vulnerability-researcher`
   mutual-exclusion rule when both are present.
