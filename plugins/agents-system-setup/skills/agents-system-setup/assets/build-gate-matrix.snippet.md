<!-- agents-system-setup:build-gate-matrix:start -->

> **The host orchestrator runs this gate on every code change.** Compute the
> diff bucket as `max(size_bucket, criticality_bucket)` per
> [SDLC Build Gate reference](https://github.com/ytthuan/agents-system-setup/blob/main/plugins/agents-system-setup/skills/agents-system-setup/references/sdlc-build-gate.md).
> Required gates are fail-closed: missing evidence blocks `@change-validator`
> sign-off.

**Strictness:** {{BUILD_GATE_STRICTNESS}}  <!-- standard | strict | light | skipped -->

### Diff buckets

- **XS** — 1 file · ≤ 10 lines · no critical-surface marker.
- **S** — ≤ 3 files · ≤ 50 lines · no critical-surface marker.
- **M** — ≤ 10 files · ≤ 200 lines, or any `M`-marker (lockfile/manifest,
  feature flag, serialization, auth-adjacent middleware).
- **L** — ≤ 25 files · ≤ 500 lines, or any `L`-marker (auth/authz, crypto,
  public API/ABI, schema/migration, permission/IaC, billing/privacy,
  CI/release, recovery/retention).
- **XL** — > 25 files or > 500 lines, or two+ `L`-markers, or any
  release-shaped change.

### Required gates per bucket

| Bucket | Build | Unit | E2E | Review | Bug hunt | Validation |
|---|---|---|---|---|---|---|
| XS | ✅ | 🟡 | n/a | ✅ | n/a | ✅ |
| S | ✅ | ✅ | 🟡 | ✅ | 🟡 | ✅ |
| M | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| L | ✅ | ✅ | ✅ | ✅ (+ security owner if security-L) | ✅ | ✅ (+ architecture if boundary) |
| XL | ✅ | ✅ | ✅ | ✅ (architecture + security mandatory) | ✅ (deep hunt; security team if dedicated) | ✅ (formal sign-off; release/CI hooks verified) |

`✅` = required · `🟡` = recommended (waivable with rationale in plan) · `n/a`
= not required by the bucket.

### Owners

| Gate | Owner |
|---|---|
| Build | `@build-runner` |
| Unit test | {{UNIT_TEST_OWNER}} |
| E2E test | {{E2E_OWNER}} |
| Code review | `@reviewer` |
| Change bug hunt | `@change-bug-hunter` |
| Validation | {{CHANGE_VALIDATOR_OWNER}} |

### Routing (when both roles exist)

- Diff-scoped logic/regression/integration/lightweight security sniff →
  `@change-bug-hunter`.
- Program-scoped threat-driven research → `@vulnerability-researcher`.
- Suspicion on a diff with a dedicated security team present →
  `@change-bug-hunter` summarizes, `@vulnerability-researcher` owns the
  deeper analysis.

### Wave assignment

- Build → Unit Test (sequential per language toolchain).
- E2E · Review · Change bug hunt (parallel wave once build/unit pass).
- Change Validation (final wave, `waits_for` every preceding gate).

<!-- agents-system-setup:build-gate-matrix:end -->
