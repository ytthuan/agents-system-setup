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

For non-software-dev projects or `Skip`, emit no full Build Gate section,
matrix, or role roster. A compact conditional status may say `n/a` where an
existing template requires a value.

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

Each bucket maps to a required gate set. The Build Gate is **fail-closed**: missing/denied canonical skill context or
missing evidence for a required gate blocks the affected code action and
validation sign-off.

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
| Build | project `build_owner` | command, exit status, build artifact paths, log summary |
| Unit test | project `unit_test_owner` | command, pass/fail counts, coverage delta if available, failing test names |
| E2E test | project `e2e_owner` | command, scenarios run, pass/fail, screenshots/traces stored path |
| Code review | project `review_owner`, independent of writer | reviewed file paths, signed-off-by, blocking comments resolved (or rationale waived) |
| Change bug hunt | project `bug_hunt_owner` | scanned paths, candidate count, suspicion list, severity, link to evidence |
| Validation | project `change_validator_owner` | aggregated gate status, required-approval status, residual risk note |

The **Code review** gate includes the maintainability / project-convention /
code-smell verdict from [code-quality](./code-quality.md), owned by
`@code-quality-reviewer` (or `@reviewer` when merged) and reported as
`Code quality: ok|warn|fail|n/a; signals=<list|none>`. That standard is the
*authoring* craft applied while the code is written; this Build Gate is the
*verification* that the change holds together. The validation owner folds the
`Code quality:` line into review evidence and never overrides the verdict.

## Strictness

User picks one in Q9d:

| Strictness | Behavior |
|---|---|
| Standard (default) | Use the matrix as written. `🟡` gates can be waived with rationale. |
| Strict | Promote all `🟡` to `✅`. XL requires two reviewer approvals and a release-validator sign-off. |
| Light | Validation merges into the independent review owner; XS keeps only build + review; M demotes e2e to `🟡`. Suitable for small teams or library code with thin runtime. |
| Skip | Do not generate Build Gate roles, snippet, or skill. Render `n/a — user skipped` in AGENTS.md. |

## Roles

The Build Gate defines logical responsibilities. Map them to existing project
roles or the host where independence is not required; emit a specialist only
when separate context, permissions, repeatability, or independent review
justifies it.

| Role | Read/Write | Owns | Boundary |
|---|---|---|---|
| Build owner | read + execute build commands | build invocation, build-output evidence | host or `build-runner`; does not change source except approved formatter output |
| Bug-hunt owner | read-only + bounded local search | diff-scoped logic, regression, integration sniff + lightweight security check | host/reviewer or `change-bug-hunter`; does not duplicate `vulnerability-researcher` |
| Validation owner | read-only + aggregate | final integration report | host/reviewer or `change-validator`; evidence integrator only |

Reuse project roles before creating specialists:

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

The Build Gate respects dependencies and adaptive delegation:

- Build and unit test follow actual toolchain dependencies.
- E2E, independent review, and change bug hunt may run concurrently after their
  prerequisites only when doing so materially helps.
- Validation waits for every required gate, whether evidence was produced by
  the host or a worker.

## AGENTS.md placement

The plugin renders the enabled Build Gate in two places:

1. **`AGENTS.md` › `## Build Gate (SDLC)`** — compact enabled-only trigger,
   strictness, logical owners, fail-closed rule, and pointer.
2. **`code-change-build-gate` skill** (per runtime, including Codex) — the one
   canonical matrix and procedure. It must be loaded before affected code work
   or sign-off; missing/denied loading blocks that action.

## Anti-patterns

- Treating size buckets as the only signal — criticality always wins.
- Letting `change-validator` override reviewer/tester correctness verdicts.
- Letting `change-bug-hunter` duplicate full threat-model analysis when a
  security team is present.
- Adding the Build Gate to documentation-only or security-team-only projects.
- Duplicating the full matrix in root memory or treating root as the conflict
  authority.
- Generating role processes solely to satisfy a fixed roster.
- Pinning concrete LOC counts inside generated AGENTS.md — use bucket labels
  and link to this reference.
- Treating ad-hoc native task-class output as gate evidence. It is
  `non-gate evidence` unless assigned through the established owning-gate
  workflow with the correct evidence and independence requirements.

## Verification

After generation, the plugin verifier confirms:

1. Enabled projects have a compact root trigger/strictness/owner/fail-closed
   pointer; skipped/non-development projects have no full gate section/roles.
2. For software-dev + not-skipped: `code-change-build-gate` skill exists at
   each selected runtime's skills path (including Codex).
3. Every required gate has a named logical owner; review is independent of the
   writer. Specialist files exist only when justified.
4. Validation waits for every required preceding gate.
5. Routing table contains the `change-bug-hunter` vs `vulnerability-researcher`
   mutual-exclusion rule when both are present.
