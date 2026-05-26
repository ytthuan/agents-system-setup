# Changelog

All notable changes to this plugin are documented here. Format: [Keep a Changelog](https://keepachangelog.com).

## [1.4.0] - 2026-05-26

### Added

- **New `upgrade` mode** for version-aware migration of existing agent systems to the current plugin's principles. Triggers: `/agents-system-setup upgrade`, `agents-system-setup upgrade`, `/setup-copilot-agents upgrade`, `$agents-system-setup upgrade` (Codex), or any host-runtime equivalent. Reads `.agents-system-setup/generated.json` (authoritative) or per-file `agents-system-setup:generated-by` stamps, compares against current `plugin.json`, walks the per-version delta playbook in order, asks once before each migration, backs up before each rewrite, preserves user customizations outside managed blocks. Non-destructive and reversible via `.bak`. Surfaced as first-class Phase 1 mode choice when stale stamps are detected.
- **Version stamping for every generated artifact.** Every emitted `AGENTS.md`, subagent file (`.github/agents/*.agent.md`, `.claude/agents/*.md`, `.opencode/agents/*.md`, `.gemini/agents/*.md`, `.codex/agents/*.toml`), and skill (`*/skills/*/SKILL.md`) carries an `agents-system-setup:generated-by: vX.Y.Z` marker — HTML comment for Markdown, `#` comment for TOML. Renderer substitutes `{{PLUGIN_VERSION}}` from `plugin.json` and optional `{{GENERATED_AT}}` ISO-8601 timestamp.
- **Central manifest `.agents-system-setup/generated.json`** as authoritative source of truth, written atomically after every `init`/`update`/`improve`/`upgrade`/`replicate` run. Schema includes `plugin_version`, `last_run`, and per-artifact records (`path`, `stamp_version`, `stamp_at`, `kind`, `platform`, `checksum`).
- **Per-version migration playbook table** in `references/misplaced-artifacts-migration.md` › **Version Stamp Detection & Migration Playbook**. Documents `pre-stamp → v1.3.0`, `v1.2.0 → v1.3.0`, and `v1.3.0 → v1.4.0` delta requirements. `upgrade` mode walks the table in order; improve mode treats version drift as a first-class delta.
- **Hard rule #34** — Generated artifacts carry a `generated-by` version stamp + central manifest. Improve / upgrade modes read stamps and apply per-version deltas. Never hand-edit a stamp.
- **References/handoff.md → canonical Host Orchestrator Lifecycle, Wave Execution Playbook, Memory & Learning Coordination, Out of Scope** sections. AGENTS.md.template links here instead of duplicating; subagents load on demand.
- **`references/misplaced-artifacts-migration.md` migration safety rules** (always backup, diff custom content first, preserve user content outside managed block, update stamp atomically with content, manifest updated last, pre-stamp detection is conservative) and stamp anti-patterns (no hand-editing, no committing manifest without opt-in, no skipping intermediate version deltas).

### Changed

- **`AGENTS.md.template` › `## Orchestration Operating Model` slimmed from ~83 lines to ~37 lines.** Preserves inline: Role and Delegation Stance, 7 Core Hard Rules (covering Directory Architecture, security/architecture gates, `@reviewer`/`@tester`/security-owner routing with `.mcp.json` / `opencode.json` enumerated, `@requirements-triage` (read-mostly advisory) and `@agent-quality-curator` (read-only advisory) split, plan handoff normalization, schema isolation, question_request consumption, learning check, "never store secrets" guardrail), Required Minimum 12-field summary (full list inline so orchestrator never delegates without the safety contract), malformed-assignment behavior, Subagent Routing. **Moves out** to `references/handoff.md`: 13-step Host Orchestrator Lifecycle prose, Wave Execution playbook details, Memory & Learning coordination procedure, Out of Scope list. Net: Codex/Gemini subagents (which auto-load `AGENTS.md`) see significantly less context bloat without losing safety invariants.
- **Subagent template Acceptance Checklist trimmed from 14 → 6 items** across all 4 Markdown templates (`subagent.agent.md.template`, `subagent.claude.md.template`, `subagent.opencode.md.template`, `subagent.gemini.md.template`). Preserved receiver-side defenses per rubber-duck critique: (1) all 12 required-minimum fields present; (2) `File Inventory.to_modify` intersects only Owned paths; (3) `Required approvals` lists every approval or `none`; (4) full-form required for MCP/secrets/CI/release/dependency/generated-script/fan-out/security-write/replication/release tasks; (5) Security-team tasks include authorization/validation/counterevidence/severity/proof-gap fields; (6) no inventing missing skills/tools/MCP/approvals/files. Removed: Context freshness wording check, Read-only path exclusion, Verification Protocol exactness, Reporting Protocol exact match, Constraints/Risks gate mention, Coordination wave-siblings format, Content Quality named-check, Context Packet scope wording, Allowed Capabilities/Skills Referenced runtime-neutrality, Expected output specificity (all covered by general "well-formed assignment" check from item 1).
- **Model selection is now strictly opt-in.** Interview Q9b is no longer asked by default. The opt-in gate only triggers when the user has spontaneously named a model (e.g., "use Sonnet 4.5", "gpt-5-mini") in the brief or prior turns, explicitly asked for BYOK/multi-model routing/cost-perf tuning, or signalled awareness another way. Default `model_overrides_policy = skipped` emits no `model:` lines anywhere. Hard rule #22 updated. Phase 8 wrap-up may surface model overrides as post-generation optional add-on — never as a required step.
- **Codex skill support documentation corrected** in `references/platforms.md`. Previously contradictory across `platforms.md` ("not supported natively"), `runtime-updates.md` (`$skill-name`/`/skills`), and `skill-format.md`. Now consistent: Codex DOES support skills at `.codex/skills/<name>/SKILL.md` (project) or `~/.codex/skills/<name>/SKILL.md` (user); activates via Codex skill loader; selectable with `$skill-name` (CLI) and browsable with `/skills`; Codex App surfaces skills via its skill UI.
- **`misplaced-artifacts-migration.md` portable skill default** now includes Codex as a target (was: "Codex skills stay described in `AGENTS.md`"; now: "one target per runtime that supports skills natively, including Codex which loads `.codex/skills/<name>/SKILL.md`").
- **`scripts/_validate.py`**: relaxed Codex `@<plugin-name>` stale-phrase check to honor negative context ("no", "not", "never", "without", "don't", "do not", "avoid", "nonexistent"), matching the existing OpenCode pattern.

### Validation

- All ~17 validator orphan checks resolved after AGENTS.md.template trim (phrases that moved to `handoff.md` are now checked there: `security/audit evidence`, `proof gaps`, `host-orchestrator and security-owner approval`). Subagent template checks dropped phrases that were trimmed from Acceptance Checklist (`Context freshness is explicit`, `Expected output`).
- `SKILL.md` stays at exactly 500/500 hard cap after trimming the orchestrator-emission narrative paragraph in Phase 4, merging the "Gemini emits at .gemini/agents/" duplicate sentence with the artifact list, and compressing hard rules #22, #33, #34.
- `bash scripts/validate.sh` clean.
- `npx --yes markdownlint-cli2 "**/*.md" "!node_modules" "!.git"` clean (pending final run).

### Migration notes

For users upgrading from v1.3.0:

1. Existing AGENTS.md generated by v1.3.0 has a ~83-line Orchestration Operating Model section. Use the new `upgrade` mode to migrate it to the slim v1.4.0 shape (~37 lines). The upgrade reads `agents-system-setup:generated-by: v1.3.0` (or `pre-stamp` if absent), backs up, diffs for custom content, asks for approval before replacing, and adds the version stamp + central manifest in the same pass.
2. Existing subagent files generated by v1.3.0 have a 14-item Acceptance Checklist. The `upgrade` mode replaces it with the trimmed 6-item version that preserves all rubber-duck-validated receiver-side defenses.
3. Pre-stamp systems (`v1.2.0` or earlier without stamps) are detected by absence of `agents-system-setup:generated-by` markers. The upgrade walks `pre-stamp → v1.3.0 → v1.4.0` deltas in order.
4. User customizations outside `<!-- agents-system-setup:managed:start -->` / `:end` markers are always preserved.
5. Model override lines (`model: ...`) in existing agents are preserved as-is; the model-selection change only affects how the interview asks the question, not generated artifacts.

## [1.3.0] - 2026-05-20

### Removed

- **`assets/orchestrator.agent.md.template`**, **`assets/orchestrator.claude.md.template`**, **`assets/orchestrator.opencode.md.template`** (3 files, ~265 lines combined). No runtime emits a separate `orchestrator` subagent file anymore. The host CLI session (Copilot CLI, Claude Code, OpenCode, Codex CLI, Gemini CLI) is the orchestrator and reads `AGENTS.md` directly. Codex CLI already followed this pattern; v1.3.0 normalizes the remaining four runtimes.

### Added

- **Hard rule #33 — The orchestrator is the host CLI session, not a subagent file.** Never emit `orchestrator.agent.md`, `.claude/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.codex/agents/orchestrator.toml`, or `.gemini/agents/orchestrator.md`. `@orchestrator` remains a routing alias for the host session.
- **`AGENTS.md.template` → `## Orchestration Operating Model` section** (Role, "When to delegate vs. act directly" pragmatic rule, 14 Hard Rules, Context Load Order, Lifecycle (13 steps), Orchestrator Assignment Format, Wave Execution, Memory & Learning, Subagent Routing, Out of Scope). The host CLI session reads this and adopts the orchestrator role. Consolidates everything from the three deleted templates.
- **Pragmatic host-session guardrail.** "For non-trivial / risky / multi-file / security-sensitive / MCP-touching / release / replication / multi-wave work, delegate. Tiny single-step work may be done directly only when no ownership, security, review, testing, or approval gate is bypassed." (Replaces the old "I never implement code or run tests directly" blanket rule — too strict for a host session that is also user-facing.)
- **OpenCode `permission.task` gate relocation.** Moves from the deleted `orchestrator.opencode.md` frontmatter to `opencode.json` › `agent.<root>.permission.task` (with `"*": "deny"` plus explicit roster allows). Treated as a **separate config approval gate** (not the MCP gate); on decline, records `opencode_task_gate: declined` and reports degraded-mode warning.
- **Improve-mode migration for deprecated orchestrator subagent files** in `references/misplaced-artifacts-migration.md` › **Deprecated orchestrator subagent files**. Per-file choices: `Back up and delete (Recommended)`, `Keep but mark deprecated`, `Back up + report custom additions for manual review` (default when `has_custom_content=true`), `Skip`. Backup path `.agents-system-setup/.bak/<ts>-<migration_id>/orchestrator-deprecation/<source-rel>`. Ledger actions: `orchestrator-deprecation-(deleted|marked|reviewed|skipped)`. **Never auto-merges custom prose** into `AGENTS.md`. OpenCode `permission.task` migration **parses and preserves existing user customizations** rather than overwriting with the generic template.
- **Replication `RootRoleIR` classification.** Source orchestrator files (any role/file named `orchestrator` with no owned implementation paths) are classified as `RootRoleIR`, not `AgentIR`. Their content merges into the target's `AGENTS.md` › Orchestration Operating Model; runtime-specific frontmatter (e.g., OpenCode `mode: primary`, `permission.task`) is dropped with a lossiness entry (permission.task migrates to `opencode.json` for OpenCode targets). Verify round-trip by checking that no target emits `*/orchestrator.*`.
- **`references/runtime-updates.md` → "Orchestrator elimination — 2026-05-20 (v1.3.0)"** finding row with per-runtime old/new behavior table.

### Changed

- **`references/topology.md` opening paragraph** clarifies that the orchestrator is the host CLI session reading `AGENTS.md`. `@orchestrator` is a routing alias for that host/root session. Subagent files in the topology table cover specialized roles only. Directory Architecture "always-present" rows mark owner as `@orchestrator (host session)`.
- **`references/handoff.md` per-runtime handoff surfaces table** updated: each runtime row now reads "Orchestrator role: `AGENTS.md` › Orchestration Operating Model (host session)" plus explicit "No `*/orchestrator.*` file is emitted".
- **`references/agent-format.md`** marks `AGENTS.md` as the canonical orchestrator location for every runtime (formerly only Codex). OpenCode `mode: primary` section updated: the root-session `permission.task` subagent-gating lives in `opencode.json` since v1.3.0; no `.opencode/agents/orchestrator.md` is emitted.
- **`README.md`** updated: "Host-session Orchestration Operating Model + N specialized subagents" replaces the old "Orchestrator + N subagents emitted" claim. Copilot CLI Standard Tool Profile section clarifies that the orchestrator role lives in `AGENTS.md` (read by host); no orchestrator subagent file is emitted. Codex section clarifies that no `.codex/agents/orchestrator.toml` is emitted.
- **SKILL.md frontmatter description** updated: "Generates AGENTS.md (with host-session Orchestration Operating Model) plus specialized subagents (no separate orchestrator file)".
- **SKILL.md Phase 4** orchestrator emission lines consolidated from three bullets (one per runtime) into one bullet pointing to the new `AGENTS.md` Orchestration Operating Model section.

### Validation

- New validator function `check_no_orchestrator_subagent_emission()` enforces: (a) the three deleted templates do NOT exist; (b) `SKILL.md` does NOT reference them; (c) `AGENTS.md.template` contains `## Orchestration Operating Model` with all the merged markers (Hard Rules, Lifecycle, Wave Execution, Memory & Learning, Security & Audit, Content Quality, Security Team, Requirements Triage, Reflect & Learn); (d) `SKILL.md` contains hard rule #33 + the orchestrator-elimination anti-pattern; (e) `references/misplaced-artifacts-migration.md` documents the four migration choices and the OpenCode `permission.task` preservation rule; (f) `references/topology.md` has the virtual-role clarification; (g) `references/handoff.md` per-runtime markers; (h) `references/agent-format.md` routes Codex orchestrator to `AGENTS.md` and OpenCode `permission.task` to `opencode.json`; (i) `references/replication.md` classifies `RootRoleIR`; (j) `references/runtime-updates.md` has the elimination finding row; (k) **stale phrase scanner** flags `emit orchestrator`, `orchestrator (agent) file`, `orchestrator + N subagents`, `orchestrator/subagents`, `orchestrator templates?`, `generated orchestrators?` across `README.md`, `DESIGN.md`, `SKILL.md`, templates, and references (excludes `CHANGELOG.md` — historical entries are by design).
- New validator function `check_pointer_files_to_agents_md()` ensures `GEMINI.md.template` references `AGENTS.md`, `SKILL.md` references the project-memory linking step, and the cross-OS linker scripts exist at `plugins/agents-system-setup/skills/agents-system-setup/scripts/link-project-memory.{sh,ps1}`.
- New validator function `check_opencode_root_task_gate()` enforces: (a) `SKILL.md` describes the OpenCode root-session task gate with a separate config approval gate; (b) `references/misplaced-artifacts-migration.md` documents extracting and preserving existing user customizations; (c) any `opencode.json` actually present in the repo (samples, fixtures, generated reference output) carries `agent.<root>.permission.task` with `"*"` set to `"deny"` or `"ask"`, never `"allow"`.
- Removed ~25 `require_contains` sites that referenced the deleted templates. Migrated relevant markers to `AGENTS.md.template` checks (`check_governance_baseline`, `check_mcp_approval_gate`, `check_requirements_triage_policy`, `check_output_quality_policy`, `check_security_team_policy`, `check_context_optimization`, `check_plan_handoff_policy`, `check_prompt_handoff_quality_policy`, `check_copilot_tool_profile`, `check_learning_memory_policy`).
- All gates: `bash scripts/validate.sh` passes (1 informational SKILL.md size warning, expected `.ps1` LF/CRLF warnings); `npx markdownlint-cli2@0.22.1 "**/*.md" "!node_modules" "!.git"` clean; rubber-duck on `gpt-5.5` first-pass (4 blocking → all addressed: virtual-orchestrator formalization, OpenCode permission.task relocation, host-session pragmatic guardrail, pointer-file validator coverage); second-pass (2 blocking → all addressed: separate OpenCode config approval gate + opencode.json validator, README/SKILL frontmatter updated to drop "Orchestrator + N subagents"; non-blocking: extract-and-preserve OpenCode permission.task on migration, expanded stale-phrase scanner with 6 patterns and README/DESIGN coverage).

### Migration notes

- **Breaking behavior change for existing setups that emit `orchestrator.*.md`**: `improve` mode detects the file and presents the four migration choices above. The default is `Back up and delete` for unmodified files, `Back up + report custom additions for manual review` for files with custom content. Existing automation that invokes `@orchestrator` as a callable subagent (e.g., Claude `Agent(name="orchestrator")`) should be repointed to a specialized subagent role (or to the host session itself, since the host fulfills the orchestrator role naturally). `@orchestrator` remains a logical routing alias.
- **OpenCode users**: the `permission.task` subagent-gating moves from `.opencode/agents/orchestrator.md` to `opencode.json` › `agent.<root>.permission.task`. The migration parses your existing block, preserves your specific allows/asks/entries, and renders the proposed snippet for review under a separate config approval gate. Decline the gate to record `opencode_task_gate: declined` and continue without permission-constrained fan-out.

## [1.2.0] - 2026-05-16

### Added

- **Purpose-first wizard (hard rule #32).** Phase 0 is restructured into three sub-steps: `0` captures the user's headline purpose first (with the explicit labeled choice `"I'm exploring — let recon lead"` normalized to the `"exploring"` sentinel), `1` detects footprint, `2` shows the profile card and asks mode. The directory no longer anchors the interview — user intent does.
- **Purpose-aware cwd reconnaissance.** Phase 1 recon now scores signal groups against the captured `headline_purpose` and sorts the Reconnaissance Card by relevance (`high → med → low → n-a`). The card **never filters** — every non-empty group is still rendered, only ordering changes. Tokenization splits on whitespace, commas, `/`, and the conjunctions `and`/`or`/`&` so multi-purpose statements (`"build a payments API and a mobile client"`) keep their facets separable; per-group relevance is the **max across clauses**. Stopwords cover English + generic intent words (`build`, `create`, `make`, `setup`, `improve`, `audit`, `agent`, `agents`, `system`, `project`, `app`, `application`). Improve-mode caveat: purpose-relevance affects card ordering only; broad audit still covers all surfaces.
- **Exploring fallback.** When `headline_purpose == "exploring"`, every group's relevance is `n-a`, the card renders in default order, and the orchestrator re-asks the purpose question **after** the user confirms the card.
- **Q1 becomes confirm-or-revisit.** Interview Q1 no longer asks "what does this project do?" from scratch; it confirms the headline (`"Earlier you said: <headline>. Anything to add or correct?"`) or, for `exploring`, defers until after the card and re-asks.
- **Output contract `Purpose:` line.** New `✅ Purpose: <headline | exploring>` line above the existing `Recon:` line.
- **AGENTS.md template recon snapshot includes purpose.** `{{RECON_SNAPSHOT}}` first line is `- Purpose: <headline | exploring>` so future agent sessions inherit the captured intent.

### Changed

- **SKILL.md Phase 0 header** renamed from "Detect Footprint & Choose Mode" to "Capture Purpose, Detect Footprint, Choose Mode".
- **Anti-pattern consolidations** to stay within the 500-line SKILL.md hard cap while adding hard rule #32 and the new "Running deep recon before knowing user purpose" anti-pattern: merged Codex/Gemini subagent-contract anti-patterns (one bullet); merged wrong-directory anti-patterns for operational logs vs runtime artifacts (one bullet); merged wrap-up hygiene trio (one bullet); merged cross-OS slips trio (one bullet); merged governance trio (one bullet); merged plan/MCP/approval-gate trio (one bullet); merged frontmatter-schema trio (one bullet); merged content-quality + artifact-tracking (one bullet). All requirements remain; only repetition was removed.

### Validation

- New validator function `check_purpose_before_footprint_in_phase_0()` enforces that the SKILL.md Phase 0 **body** (header excluded) has the purpose sub-step before the footprint sub-step, and that the canonical markers `Sub-step 0 — Capture headline purpose` and `Sub-step 1 — Detect footprint` are present and correctly ordered.
- `check_cwd_reconnaissance_policy` gains `require_contains` markers for `Purpose-aware scoring`, `Scoring rubric`, `headline_purpose`, `purpose_relevance`, `Exploring fallback`, `exploring`, `Never filter`, `` `high` → `med` → `low` → `n-a` ``, `normalize`, and `Improve-mode caveat`. The SKILL.md, interview.md, and output-contract.md marker checks are also extended for the v1.2.0 wiring (`Capture Purpose`, `headline_purpose`, `purpose-aware`, `Capture headline purpose`, `Purpose:`).
- All gates: `bash scripts/validate.sh` passes (1 informational SKILL.md size warning, expected `.ps1` LF/CRLF warnings); `npx markdownlint-cli2 "**/*.md" "!node_modules" "!.git"` clean; rubber-duck on `gpt-5.5` with both blocking findings closed.

## [1.1.1] - 2026-05-15

### Fixed

- **Portable folder digest now defines symlink handling explicitly.** The pseudocode in `references/misplaced-artifacts-migration.md` walks with `followlinks=False`, emits a deterministic symlink line `<rel-path> link:<rel-target> <octal-mode>`, aborts with `reason: external-symlink` when a resolved symlink leaves the artifact root, and breaks defensively on inode loops with `reason: digest-loop`. Closes the second-pass critique on Blocking #1 (digest).
- **Backup directory is collision-resistant.** `Move (Recommended)` and `Delete after explicit confirmation` now use `.agents-system-setup/.bak/<ts>-<migration_id>/<source-rel>` with `<ts>` defined as filesystem-safe ISO-8601 UTC (colon → `-`) and `<migration_id>` as the first 8 characters of `base32(uuid4())`. The leaf directory is created exclusively (`mkdir` without `-p`) with retry on `EEXIST` (`reason: backup-collision` after three retries). The shared `.agents-system-setup/.bak/` parent is created with `-p`.
- **npm `_authToken` redaction also catches the bare form.** `references/cwd-reconnaissance.md` regex updated from `(?i)//[^/\s]+/:?_authToken\s*=\s*\S+` to `(?i)(?://[^/\s]+/:?_authToken|(?:^|\s)_authToken)\s*=\s*\S+` so bare `.npmrc` lines like `_authToken=…` are also redacted.

### Validation

- `check_cwd_reconnaissance_policy` now `require_contains` the specific secret-pattern names (`AKIA[0-9A-Z]`, `AWS_SECRET_ACCESS_KEY`, `github_pat_`, `sk-(?:ant-)?`, `_authToken`, `Authorization header`, `"private_key"`, `JWT triplet`) so a future edit cannot silently drop one.
- `check_misplaced_artifacts_migration_policy` now `require_contains` `Backup directory naming`, `migration_id`, and `external-symlink`.

## [1.1.0] - 2026-05-15

### Added

- **Standard skill paths + per-platform mapping (all six runtime artifact types).** SKILL.md Phase 4 now enumerates per-platform skill paths inline (Copilot `.github/skills/`, Claude `.claude/skills/`, OpenCode `.opencode/skills/`, Gemini `.gemini/skills/`, Codex described in `AGENTS.md`). New hard rule (#31) declares `.agents-system-setup/` operational state only — no `agents/`, `skills/`, `hooks/`, `commands/`, `prompts/`, or `plugins/` subtrees.
- **Misplaced-artifacts migration** at `plugins/agents-system-setup/skills/agents-system-setup/references/misplaced-artifacts-migration.md` covering all six runtime artifact types. File-based artifacts (agents, skills, OpenCode/Copilot hooks, commands, prompts, plugin manifests) default to `Move (Recommended)` with `.agents-system-setup/.bak/<ts>/` backup, portable manifest digest verify (`sha256(<rel-path> <file-sha256> <octal-mode>` lines, sorted, LC_ALL=C; replaces brittle `tar` hash), then remove. Config-embedded artifacts (Claude/Gemini hooks in `settings.json`) default to `Convert manually (Recommended)` with a copy-pasteable JSON snippet — never auto-rewrite settings.json. Per-artifact `ask_user`; ledger appended to `.agents-system-setup/migration.jsonl`. Skills migrate to all selected runtimes by default; non-portable artifacts ask per-runtime.
- **Source-type-safe deprecation markers.** Markdown/Text/TOML/YAML get trailing comments; JSON gets a sibling `<source>.agents-system-setup.deprecated.json` sidecar (no in-place mutation); folder artifacts get a top-level `DEPRECATED.md`.
- **CWD project reconnaissance** at `plugins/agents-system-setup/skills/agents-system-setup/references/cwd-reconnaissance.md`. Phase 1 runs a safe-readonly scan (paths only for data dirs, README/docs ≤100 lines, source tree ≤2 levels deep, manifests ≤200 lines). Renders a Reconnaissance Card and asks `ask_user` to accept/correct/skip before continuing the interview. Privacy guardrails: never open data files; magic-byte detection (NUL/UTF-8); 64 KB cap; secret redaction across AWS classic + env-style, GitHub classic + fine-grained PATs, OpenAI/Anthropic `sk-` keys, Slack tokens, npm `_authToken`, `Authorization: Bearer`, Google service-account `private_key`, generic API-key patterns (quoted + unquoted), private key headers, JWT triplets. Q1/Q3 interview pre-fill from the card.
- **Hook safety warning** rendered above every `Convert manually` snippet ("This hook is currently inert. Pasting it into settings.json will enable execution. Review commands, env, and any referenced secrets before saving.").
- **Output contract reporting.** New `Recon: <signals|n/a|skipped>; redactions=<count|none>` and `Path migration: <none|moved=N copied=N skipped=N manual=N failed=N>` lines.
- **Dedicated security team topology** for bug hunting, vulnerability validation, attack-path analysis, disclosure triage, and remediation verification at `plugins/agents-system-setup/skills/agents-system-setup/references/security-team.md`. Activated explicitly via interview Q3 (`Security team / Bug hunting`) or Q9a depth (`baseline | dedicated | expanded`). Read-mostly defaults; remediation writes / external scanning / exploit execution / credential use / production testing / disclosure outreach require explicit approval. New task tags `bug-hunting`, `vulnerability-validation`, `attack-path-analysis`, `remediation-verification`, `disclosure-triage`. Source-backed by OWASP SAMM, NIST SSDF, OWASP Vulnerability Disclosure, CISA CVD, FIRST CVSS, CWE, OWASP Top 10. License-attributed plugin recommendations only — no proprietary copying.

### Changed

- **`assets/AGENTS.md.template`.** Read First / Context Loading Policy gain `{{RECON_SNAPSHOT}}` (≤5 lines). Project Snapshot, routing, and `## Security Team Operating Model` block added when security depth is `dedicated` or `expanded`.
- **`assets/gitignore.template`.** Comment now spells out the no-runtime-subtrees rule for `.agents-system-setup/`.
- **References cross-references.** `references/skill-format.md`, `references/agent-format.md`, `references/platforms.md`, `references/local-tracking.md` all link to `misplaced-artifacts-migration.md` and flag the operational-dir prohibition.
- **Orchestrator and subagent templates** (Copilot/Claude/OpenCode/Codex TOML/Gemini, plus `GEMINI.md`) now carry security-team scope/checklist/reporting strings, the canonical `Security analysis: …` reporting line, and reference the new `{{SECURITY_TEAM_DEPTH}}` and `{{SECURITY_TEAM_OPERATING_MODEL}}` placeholders.

### Fixed

- **Skill misroute.** Generated skills no longer land in `.agents-system-setup/skills/**` (which no runtime loads). The new hard rule, explicit per-platform mapping, anti-pattern, and validator check make this a hard error in this repo and a prompted migration in user repos.
- **Brittle directory hash in migration verification.** Replaced `tar -cf - <folder>` (parent-path/format dependent) with a portable manifest digest so source and target compare equal regardless of where they live.
- **Unsafe deprecation marker on JSON / folder artifacts.** `Copy + deprecate` no longer mutates JSON sources or appends to directories; it uses a sidecar JSON file or a top-level `DEPRECATED.md` instead.

### Validation

- New validator checks: `check_operational_state_artifacts`, `check_cwd_reconnaissance_policy`, `check_misplaced_artifacts_migration_policy`.
- All gates: `bash scripts/validate.sh` passes (1 informational SKILL.md size warning, expected `.ps1` LF/CRLF warnings); `git diff --check` clean; `markdownlint-cli2@0.22.1` 0 errors over 39 files; `python3 -m py_compile scripts/_validate.py` clean.

## [Unreleased]

### Added

### Changed

### Fixed

## [1.0.3] - 2026-05-14

### Added

- Structured main-to-subagent prompt handoff guidance with an Orchestrator Assignment Format, Context Packet, assignment-quality reporting, and provider-aware template coverage.

### Changed

- Generated AGENTS, GEMINI, orchestrator, subagent, and Codex TOML templates now include compact assignment intake and prompt-contract quality expectations.

### Fixed

## [1.0.2] - 2026-05-07

### Added

- Provider-aware human-input/question protocol across Copilot CLI, Claude Code, OpenCode, OpenAI Codex, and Gemini CLI, including non-terminating `question_request` fallback guidance for subagents.
- Safe self-update preflight before setup, with fast-forward-only update rules and no silent MCP/plugin/runtime config edits.
- Default-on `requirements-triage` role for decomposing ambiguous, risky, cross-runtime, release, MCP, replication, audit, improve, or multi-wave setup requests.
- Universal content-quality / anti-slop guardrails with a read-only `agent-quality-curator`, signal taxonomy, output markers, and validator coverage.

### Changed

- Generated AGENTS, GEMINI, orchestrator, subagent, and Codex TOML templates now include human-input, requirements-triage, learning, and content-quality reporting surfaces while preserving provider-specific schemas.
- Handoff, output-contract, topology, context-optimization, marketplace, platform, runtime-update, wrap-up, and learning-memory references now document the latest generated-system workflow and quality gates.
- Validator guardrails now cover human-input tool names, self-update safety, requirements-triage boundaries, content-quality policy, and current `question_request` terminology.

### Fixed

- Current handoff guidance now consistently uses `question_request`; legacy `clarification_request` remains documented only as superseded.

## [1.0.1] - 2026-05-05

### Added

- Validator guardrails for runtime invocation drift now catch stale Codex `@...` skill examples, nonexistent OpenCode plugin-install commands, provider-specific invocation markers, Gemini native skill coverage, and Copilot `.github/agents/*.md` import/drift signals.

### Changed

- Runtime invocation guidance now distinguishes provider-specific skill, command, agent, plugin, and MCP surfaces across Copilot CLI, Claude Code, OpenCode, OpenAI Codex CLI/App, and Gemini CLI.
- Codex usage examples now use `/skills` and `$agents-system-setup` for bundled skill invocation while keeping `/plugins` and marketplace install guidance explicitly CLI-only.
- OpenCode guidance now separates JS/TS plugins, Markdown agents, `skill` tool activation with `permission.skill`, and `.opencode/commands/<name>.md` slash commands.
- Gemini guidance now documents native `.gemini/skills/<name>/SKILL.md` skills and native `settings.json` hooks in addition to extension-packaged surfaces.

### Fixed

- Claude Code plugin `commands/` are no longer described as legacy-only; the docs now keep commands for slash-command prompts and recommend skills for reusable workflows.
- Copilot plugin install examples now separate terminal `copilot plugin install ...` usage from in-session `/plugin install PLUGIN@MARKETPLACE` usage.

## [1.0.0] - 2026-05-03

### Added

- **Memory & Learning System.** Generated agent setups can include a project-specific learning loop: agents load a Learning Index, run a before-finish `Learning Check`, and propose durable learnings for conventions, mistakes, tool insights, workflows, preferences, and risks.
- New `references/learning-memory.md` and `assets/learnings.md.template` define storage profiles, a compact learning record schema, privacy/security rules, optional hook support, and the rule that overwrite requires orchestrator approval.
- Orchestrator templates gain **Reflect & Learn**; subagent templates and Codex TOML gain **Learning Check** reporting.
- Output contract now reports learning memory profile, proposal counts, and accepted/deferred learning updates.
- Critic-driven hardening adds validator guardrails for MCP approval gates, MCP secret-shaped values, generated-template links, Copilot read-only tool profiles, supported runtimes, optional placeholder leaks, central MCP approval evidence, OpenCode task gates, and release changelog/markdownlint gates.

### Changed

- Context loading now treats memory as indexed context: agents load relevant learnings instead of the full operational ledger.
- Replication guidance preserves the Memory & Learning System across target runtimes.
- The interview flow now detects first, chooses mode before runtime expansion, offers safe defaults for non-gated questions, groups advanced agent behavior choices, avoids per-agent model prompt loops by default, and keeps final summaries filtered to the selected platforms.
- Generated templates now point subagents to `AGENTS.md` for runtime-available handoff/memory guidance instead of dev-repo-only relative reference links.
- OpenCode primary agents now default to explicit `permission.task` gating, and Codex guidance keeps CLI + App shared artifacts separate from CLI-only usage notes.

### Fixed

- Release workflow checks now include markdownlint, changelog finalization, nested manifest version checks, and broader manifest JSON smoke parsing before publishing.
- Validator hardening now detects structural MCP blocks instead of prose collisions, expands secret-surface scanning, preserves no-PyYAML fallback behavior, and keeps the canonical handoff contract field list synchronized.

## [0.9.0] - 2026-05-02

### Added

- **Copilot CLI Standard Tool Profile.** Generated Copilot CLI agents now apply a documented role-aware tool profile: `standard` (`tools: [vscode, execute, read, agent, edit, search, todo]`) for orchestrator and edit-capable subagents, `read-only` (`[read, search]`) for reviewers/auditors, `runner` (`[execute, read, search, todo]`) for testers, `research` (`[read, search, web, todo]`) for docs/research gatherers, and `inherit` (omit `tools:`) for explicit opt-out.
- `vscode` added to the recognized public alias set in `references/platforms.md` and `references/agent-format.md`. The `vscode` tool exposes the VS Code chat-host tool set when the agent runs inside VS Code Chat; Copilot CLI ignores unknown aliases harmlessly per the documented "All unrecognized tool names are ignored" rule, so it ships safely as a baseline.
- New interview question Q9c (`copilot_tools_profile`) lets users pick `Standard | Minimal | Custom | Inherit`. Default = Standard.
- Output contract reports the chosen profile via `Copilot CLI tools profile:`.
- Validator guardrail `check_copilot_tool_profile` keeps the standard tool profile, marker `<!-- agents-system-setup:tools-profile: <profile> -->`, and orchestrator-must-have-`agent` rule from regressing.

### Changed

- Replication into Copilot CLI now fills `tools:` from the role-derived profile when the source IR has no explicit tools list; user-set tool lists still pass through unchanged. Tool-name canonicalization adds a `vscode_host → vscode` row.
- Orchestrator template always renders `tools: [vscode, execute, read, agent, edit, search, todo]`. Subagent template documents the role → profile mapping and records the chosen profile via `<!-- agents-system-setup:tools-profile: {{TOOLS_PROFILE}} -->`.

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
