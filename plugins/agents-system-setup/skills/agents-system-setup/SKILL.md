---
name: agents-system-setup
description: 'Bootstrap, improve, replicate, or upgrade native-first agent systems across Copilot CLI, Claude Code, OpenCode, OpenAI Codex (CLI + App), and Gemini CLI. Synthesizes compact AGENTS.md, thin adapters, on-demand skills, and justified specialists with adaptive quality/cost-aware delegation. Uses Canonical IR, approval-safe repair, MCP gates, native formats, and output-budget enforcement. Triggers: "set up agents", "scaffold AGENTS.md", "improve my agents", "audit agent setup", "architecture review", "security audit agents", "replicate agents", "upgrade agents", "agents-system-setup upgrade", "configure copilot/claude/opencode/codex/gemini", "discover plugins/MCP".'
argument-hint: '[init | update | improve | replicate | upgrade] (omit to auto-detect)'
---

# Setup Copilot Agents (multi-platform)

Synthesize one compact `AGENTS.md` from repository evidence and the active harness's native initialization output. Emit thin runtime adapters, on-demand skills, and specialists only when justified. Keep ownership and critical gates resident; keep detailed governance and procedures local and loadable. The host CLI session is the orchestrator, never a generated orchestrator file.

## When to Use

- Brand-new repository needs an agent setup from scratch (**init**)
- Existing project should adopt or extend the orchestrator + subagent pattern (**update**)
- Existing agent system needs an audit (**improve**) or a version-aware migration to current principles (**upgrade** — triggered by `agents-system-setup upgrade`)
- Agents authored for one runtime need to be ported to another (**replicate** — Copilot ↔ Claude Code ↔ OpenCode ↔ OpenAI Codex ↔ Gemini)
- Discovering relevant plugins / MCP servers from the well-known marketplaces

## Hard Rules

1. **Always interview first** with the provider-native human-input tool. Use [human input](./references/human-input.md); in Copilot CLI this is the session `ask_user` tool and `--no-ask-user` disables it. Never assume project type, language, scope, or target platform.
2. **Detect existing agent footprint on entry.** If any of `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `opencode.json`, `.github/agents/`, `.claude/agents/`, `.opencode/agents/`, `.codex/agents/`, `.gemini/agents/`, `~/.codex/AGENTS.md` exists, present mode choice with `improve` and `replicate` as first-class options — never silently jump to `update`.
3. **Task-based topology.** The host may work directly; zero specialists is valid. Generate or invoke a worker only for justified specialization, independent review, or substantial separable work. Required responsibilities and independent gates remain mandatory.
4. **Directory Architecture is generated and enforced.** Every subagent file references it; the orchestrator routes by ownership.
5. **Per-item opt-in recommendations.** Plugin / skill / MCP candidates are always presented with rationale and explicit `ask_user` choice — never bulk-applied silently.
6. **MCP config approval gate.** Before writing any MCP config (`.mcp.json`, `opencode.json` › `mcp`, agent `mcp-servers:` / `mcp_servers:`, extension/plugin MCP manifests), render the proposal and call `ask_user` for approval. No silent MCP writes — ever. Replication re-triggers this gate per new target.
7. **Marketplace-first lookup with vendor attribution.** Recommendations come from registries listed in [marketplaces](./references/marketplaces.md), tagged `[Tier · Vendor]` — never invent names or URLs.
8. **Replication goes through Canonical IR, not pairwise mappings.** See [replication](./references/replication.md). Never write a Copilot→Claude (or any other direction) function; always parse → IR → emit.
9. **Non-destructive updates.** Propose replacements before rewriting user-authored content. Record approved paths, preimages, and non-overwriting backups; stop for symlinks, collisions, or concurrent edits. A backup is not approval and must never restore stale content over newer user work.
10. **Multi-platform aware.** Emit per-platform paths and frontmatter per [platforms](./references/platforms.md). Never write Copilot frontmatter into a Claude file.
11. **Cross-OS aware.** Detect host OS once (Linux / macOS / Windows-bash / Windows-pwsh) per [cross-platform](./references/cross-platform.md). Pick `.sh` for POSIX shells, `.ps1` for native PowerShell. Forward slashes in generated docs. Never symlink on Windows. Bundle `.gitattributes` so line endings stay correct on every clone.
12. **Git is optional and gated by `ask_user`.**
13. **Parallelism needs a benefit, not a quota.** Use disjoint ownership and dependency-aware waves for substantial independent tasks when quality/context/latency benefits justify cost. Direct or sequential work is valid. Preserve optional Copilot-app cross-session advisory, `advisory_supervision`, plan gates, premise-only steering, banned polling, and branch/PR wave reconciliation per [parallelism](./references/parallelism.md); absent app tools mean `n/a`, never simulated. Claude Agent Teams remain opt-in.
14. **If the project domain is software-development, recommend GitHub Spec-Kit.** After domain detection (Phase 1.7), if the brief matches a software-dev keyword set, present spec-kit as an opt-in companion via `ask_user`, never auto-install. See [spec-kit](./references/spec-kit.md).
15. **Governance concerns are mandatory, not repeated manuals.** Preserve the Security & Audit Matrix, Threat Model, Architecture & Design Pattern decisions, ADR plan, and Quality Gates from [security-audit-architecture](./references/security-audit-architecture.md). Root memory keeps active control/owner/approval/gate summaries; full matrices and rationale live in approved local project policy. Merge roles when valid, never required independent review.
16. **Security-sensitive writes require evidence.** MCP config, secrets-adjacent paths, CI/release config, and generated scripts must have an owner, approval state, and verification evidence in the output contract. No broad write permissions without rationale.
17. **Improve / upgrade are evidence-based.** Score security boundaries, secrets, audit evidence, architecture ownership, instruction-memory conflicts/redundancy, design patterns, and supply-chain trust before applying deltas; use [instruction-memory-audit](./references/instruction-memory-audit.md).
18. **Enforce complete-file memory budgets.** Target 80-120 physical lines; every synthesized `AGENTS.md` must be at most **150 lines AND 12,288 UTF-8 bytes**, including preserved content, in Balanced/Compact/Full. This is plugin policy, not an OpenAI limit. Use [context optimization](./references/context-optimization.md) and its [placement rule](./references/context-optimization.md#2a-placement-rule--where-a-piece-of-knowledge-goes): keep routing, ownership, critical controls and gate triggers resident; put project-specific some-task knowledge in user-owned `skill-kind: domain` skills and generic craft in host skills. Never truncate or overwrite domain bodies to pass.
19. **Ask whether agent artifacts are git-tracked or local-only.** Before writing project-scoped agent files, ask the tracking question from [local tracking](./references/local-tracking.md). For local-only project files, write `.git/info/exclude` (never `.gitignore`) and verify with `git check-ignore`.
20. **Plan handoff is normalized before emission.** Treat VS Code `plan` prompt output, Spec-Kit `/plan`, and user-written plans as upstream planning input only. Convert them to the [handoff contract](./references/handoff.md) / HandoffIR, then emit each selected runtime's native format. Never copy prompt frontmatter or another runtime's agent schema into generated artifacts.
21. **Runtime drift is source-backed and gated.** Use [runtime updates](./references/runtime-updates.md) before changing platform support. Gemini CLI is supported for local project subagents; remote A2A/extension packaging surfaces remain explicit import/package work.
22. **Adaptive balanced model selection, explicit pins preserved.** Omit static model/effort fields unless pinned. At delegation, use available runtime controls to balance task difficulty, risk, quality, cost, retries, and latency within explicit pins, approved providers, and budgets. Inheritance is not necessarily cheap. Load [models](./references/models.md); never invent model IDs, effort levels, prices, or RPM/TPM. Ask interview Q9b about overrides only when the user requests them; no default per-agent model questionnaire.
23. **Task assignments use the canonical contract.** Compose every orchestrator → subagent handoff with the [Task Assignment Contract](./references/handoff.md#delegation-packet-canonical-schema). Always fill the Required Minimum; add Expansion Blocks per the [Recommended Packet Form](./references/handoff.md#recommended-packet-form). Subagents run the Acceptance Checklist before doing work and emit results via the Reporting Template; missing required fields trigger one consolidated `question_request:` to the orchestrator.
24. **Learning memory is approval-safe and native-aware.** When enabled, generated agents run the [Learning Check](./references/learning-memory.md#learning-check-contract) before final response. `none` is valid. Subagents propose learnings; only the orchestrator or memory owner writes plugin-managed memory, and overwrite requires orchestrator approval. Native provider memory is complementary and used only where documented; never emit unsupported memory fields such as Codex agent TOML `memory`.
25. **Human-input schemas are provider-specific.** Never add `ask_user` to Copilot custom-agent `tools:` profiles. Claude agents that need to ask include `AskUserQuestion`; OpenCode uses nested `permission: { question: allow }`; Codex uses `request_user_input` only in Plan mode and falls back to `question_request`; Gemini may allow `ask_user`. Subagents return `question_request` when they cannot ask directly.
26. **Run self-update preflight before setup.** Phase -1 uses [self-update preflight](./references/self-update-preflight.md) at `${AGENTS_SYSTEM_SETUP_HOME:-$HOME/github/agents-system-setup}`. Fast-forward only clean Git checkouts; ask or emit `question_request` on dirty, missing, divergent, or install-manager ambiguity. Never update MCP/plugin config silently.
27. **Triage is a responsibility, not a compulsory worker.** Resolve ambiguity and scope before planning; merge `requirements-triage` into the host/planner unless separate read-mostly context is useful. Use `question_request`; triage never owns final decisions or approval gates.
28. **Content quality is universal.** Apply [content quality](./references/content-quality.md) to generated agents, skills, memory, recommendations, and output contracts. Merge review into the host/reviewer unless a separate read-only `agent-quality-curator` is justified; preserve required independence and report `Content quality: ok|warn|fail|n/a`.
29. **Main-to-subagent handoff is structured.** Use the [handoff contract](./references/handoff.md) and [prompt guidelines](./references/prompt-guidelines.md) to compose provider-native Task Assignments. Recommended-only for safe tiny work; full-form for normal, risky, multi-file, fan-out, MCP, release, replication, security, architecture, or generated-agent-system work. Pass a subtask slice, not full project memory.
30. **Dedicated security teams are explicit.** Generate the [security team](./references/security-team.md) topology only when the user selects `Security team / Bug hunting`, asks for bug hunting/security analysis/disclosure triage, or the risk intake justifies it. Security discovery, validation, attack-path, triage, and compliance roles are read-mostly by default; remediation writes, external scanning, exploit execution, credential use, production testing, disclosure outreach, MCP/tool config, and destructive tests require explicit approval and owning-agent routing.
31. **Operational state directory is artifact-free.** `.agents-system-setup/` holds operational state only (replication ledger, MCP approval evidence, learning ledger, `migration.jsonl`, `.bak` files). Never write `agents/`, `skills/`, `hooks/`, `commands/`, `prompts/`, or `plugins/` subtrees inside it; runtimes do not load them and existing misroutes go through [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md).
32. **Capture user purpose before deep recon.** Phase 0 sub-step 0 asks the headline purpose first; Phase 1 recon then **scores and highlights** signals against that intent (never filters). Allow an explicit `"I'm exploring — let recon lead"` sentinel that defers the purpose ask until after the card. See [cwd-reconnaissance](./references/cwd-reconnaissance.md#purpose-aware-scoring).
33. **The orchestrator is the host CLI session, not a subagent file.** Never emit `orchestrator.agent.md`, `.claude/agents/orchestrator.md`, `.opencode/agents/orchestrator.md`, `.codex/agents/orchestrator.toml`, or `.gemini/agents/orchestrator.md`. The Orchestration Operating Model lives in `AGENTS.md` and is read by the host CLI session of any selected runtime. `@orchestrator` remains a routing role alias for that host session — it is never an emitted agent artifact. OpenCode's `permission.task` gate moves to `opencode.json` (host root agent) since no orchestrator file is emitted.
34. **Generated artifacts carry a `generated-by` version stamp + central manifest.** Every emitted Markdown/TOML artifact includes `agents-system-setup:generated-by: vX.Y.Z` (renderer substitutes `{{PLUGIN_VERSION}}` from `plugin.json`); `.agents-system-setup/generated.json` holds the authoritative manifest. Improve / upgrade modes read stamps and apply the per-version delta playbook in [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md#version-stamp-detection--migration-playbook). Never hand-edit a stamp. The read-only `agents-doctor` skill/script reconciles on-disk agents against this manifest — strays (including a hand-written `orchestrator`), missing artifacts, checksum drift, missing stamps — and is re-runnable by a human, CI, or the host session; see [agents-doctor](./references/agents-doctor.md).
35. **SDLC Build Gate is software-dev default-on, with `Skip` opt-out.** Ask Q9d (`Standard | Strict | Light | Skip`). Unless skipped, emit discoverable `code-change-build-gate` with its full matrix and a fail-closed root trigger. Compute `max(size_bucket, criticality_bucket)`; assign build-runner, change-bug-hunter, change-validator and other gate responsibilities to justified existing/host/specialist owners. Required independent review stays independent. Missing skill, approval, or evidence blocks work/sign-off. See [sdlc-build-gate](./references/sdlc-build-gate.md).
36. **`task-delegation` is the host workflow; subagents are executors.** Make the skill discoverable for every selected runtime and load it before composing assignments. `Skills Referenced: task-delegation loaded=true` records a host load, not child content: pass required excerpts or use supported child loading. Workers keep inline fail-closed Acceptance Checklist + Reporting Template; they never re-delegate and `return-to-orchestrator` for scope gaps. Recognize `task-handoff` / `host-handoff` only as legacy migration inputs.
37. **Self-contained workers, honest context.** Every worker retains owned paths, intake, safety, reporting and the managed project-standard digest (`<!-- subagent-digest:managed:start v=<hash> --> ... :end -->`): five lines, or three for Codex. Audience labels and a parent's `recent` snapshot do not remove loaded tokens or transfer context. Per-heading markers and a separate Self-Contained Notice are not required. See [audience tags](./assets/audience-tags.snippet.md), [digest](./assets/project-standard-digest.snippet.md), and [explorer agents](./references/explorer-agents.md).
38. **Native Runtime Agents routing is optional and host-only.** When useful, render a <=5-line `{{HOST_BUILTINS_ROUTING_BLOCK}}` under Orchestration Operating Model, preserving `<!-- agents-system-setup:host-builtins-routing -->`; all profiles put runtime details in `task-delegation`. Follow [host-builtins-routing](./references/host-builtins-routing.md): ad-hoc task-class output is `non-gate evidence`; required evidence stays with assigned gate owners. Workers never re-delegate. OpenCode named built-in allows require its task gate, or record `host_builtins_routing: declined`.
39. **Tool catalog discipline.** Generated agents' tool configurations MUST match runtime-correct names in [tool-catalog](./references/tool-catalog.md) (canonical data: `assets/tool-catalog.json`). At emit time, include only tools with `scope: both` by default; `cli-only` (Copilot CLI) and `vscode-only` (VS Code Copilot) tools require explicit opt-in for the shared `.github/agents/*.agent.md` file. Per-runtime `audit_kind` differs: Copilot/Claude/Gemini = name-allowlist (validate every `tools:` / `tool_allowlist` entry against the runtime block); OpenCode = permission-policy (validate `permission:` map keys, not the deprecated `tools:` key); Codex = n/a unless `tool_allowlist` is explicitly set. Stamp every generated agent with `<!-- agents-system-setup:tool-catalog-version: <plugin-version> -->` so upgrade mode can distinguish current-catalog vs pre-catalog files. Audit skill `tool-catalog-audit` is host-side and read-only; subagents never invoke it (hard rule #36). Migration auto-classifies tool changes as `manual-review` because tool allowlists are security boundaries.
40. **Code quality & maintainability is mandatory for software-dev.** Generated coding agents **conform to the project's existing conventions first**, applying [code-quality](./references/code-quality.md) **while writing**. Mirror Build Gate strictness, floor to `light` when skipped, use `advisory` for non-software-dev source and `n/a` without source. Emit discoverable `code-quality` plus a compact root trigger; assign maintainability review to an appropriate owner without forcing another worker. `Skills Referenced: code-quality loaded=true` is host evidence; supply the child's standards. Preserve `Code quality: ok|warn|fail|n/a` and independent review.
41. **Native output first, approval before initialization.** Use [native initialization](./references/native-initialization.md) for the active harness only. Existing/custom memory is audit input, not permission to rerun `/init` over it. Copilot defaults to the root-`AGENTS.md` request; ask only if unsupported/conflicting. Record requested and observed paths separately; disclose fallback and never claim ordinary prompt text executed a native command.

## Procedure

### Phase -1 — Self-Update Preflight

Run [self-update-preflight](./references/self-update-preflight.md) before footprint
detection: only a clean upstream checkout that is behind may use `git fetch` and
`git merge --ff-only`. Other states require native human input or
`question_request`; continue with the installed version when interaction is disabled.
Never edit MCP/plugin/runtime config, generated artifacts, or release metadata here.
Record `update_preflight_status`, source path/manager and evidence in the report.

### Phase 0 — Capture Purpose, Detect Footprint, Choose Mode

**Sub-step 0 — Capture headline purpose first.** Before any directory
scan or mode choice, ask the user's intent with the provider-native
human-input tool:

> "In one sentence, what are you trying to achieve with an agent system here?"
> Freeform; offer `"I'm exploring — let recon lead"` as a labeled choice.

Persist `headline_purpose: string | "exploring"`. This drives Phase 1
purpose-aware recon scoring — see
[cwd-reconnaissance](./references/cwd-reconnaissance.md#purpose-aware-scoring).
When `exploring`, defer the purpose ask until after the recon card.

**Sub-step 1 — Detect footprint.** Inspect cwd for project and agent
artifacts per Phase 1 step 1; do not run deep recon yet.

**Sub-step 2 — Show profile card and ask mode.** Display the captured
`headline_purpose`, detected project type, existing agent artifacts by
runtime, recommended mode, and inferred current runtime(s):

> "I detected `<footprint>`. How should I proceed?"
> Choices: `["Improve current setup (Recommended when artifacts exist)", "Init new setup", "Replicate / sync to another runtime", "Update managed blocks", "Cancel"]`

Persist the selected mode. Do **not** ask target runtimes before this mode
choice. After mode is known:

- `init` / `update`: ask which runtime(s) to generate unless the user's request already names them.
- `improve`: default scope to detected runtime(s); ask a target runtime only if updating one runtime or expanding audit scope requires it.
- `replicate` / `sync`: defer source and target runtime questions to Phase 1.5, and ask targets only for the requested expansion/sync.

All later phases loop over the selected or detected runtime scope using [platforms.md](./references/platforms.md) as the source of truth for paths and frontmatter. Gemini CLI emits local subagents at `.gemini/agents/*.md`; see [agent format](./references/agent-format.md) for its non-recursive subagent and `mcp_servers:` rules.

### Phase 1 — Footprint Details & Interview Continuation

1. **Inspect cwd** and detect runtime footprint:
   - Project files: `package.json`, `*.csproj`, `Package.swift`, `build.gradle`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `mkdocs.yml`, `.git/`.
   - Agent artifacts (per runtime):
     - Copilot CLI: `AGENTS.md`, `.github/agents/*.agent.md`, `.github/agents/*.md` (docs-drift import signal), `.github/skills/`, `.mcp.json`
     - Claude Code: `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/settings.json`
     - OpenCode: `opencode.json`, `.opencode/agents/`, `.opencode/skills/`
     - OpenAI Codex: `AGENTS.md` (orchestrator + project rules), `.codex/agents/*.toml` (specialized subagents), `.codex/config.toml`, `~/.codex/AGENTS.md`, `~/.codex/agents/`; CLI-only plugin/command UX stays documented separately
     - Gemini CLI: `GEMINI.md`, `.gemini/agents/*.md`, `.gemini/settings.json`, `~/.gemini/GEMINI.md`, `~/.gemini/agents/`
   - **Project recon**: use safe-readonly [cwd reconnaissance](./references/cwd-reconnaissance.md), scoring against Phase 0 `headline_purpose`: signals are sorted `high → med → low → n-a` by `purpose_relevance`, never filtered. For `exploring`, render default order and re-ask purpose after card confirmation. Show the Reconnaissance Card and accept/correct/skip. Preserve no-data-read, magic-byte, and secret-redaction guards. Use [explorer agents](./references/explorer-agents.md) only when substantial independent recon benefits from separate context; size thresholds are hints, not forced delegation.
   - **Misplaced artifacts**: scan for `.agents-system-setup/{agents,skills,hooks,commands,prompts,plugins}/` and queue every match for the per-artifact prompt in [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md).
2. **Confirm the Phase 0 mode** — do not re-ask target runtimes before the mode
   choice. Use this table only to pick the recommended mode/default choices shown
   in the Phase 0 profile card, or to re-prompt if the initial detection was
   ambiguous:

   | Detected footprint | Default offer | Choices |
   |---|---|---|
   | Nothing | `init` | `["Init (Recommended)", "Cancel"]` |
   | One runtime, looks healthy | `improve` | `["Improve current setup (Recommended)", "Upgrade (apply version migrations)", "Update (regenerate managed blocks)", "Replicate to another runtime", "Init alongside (additive)"]` |
   | One runtime, gaps | `update` | `["Update (Recommended)", "Upgrade (apply version migrations)", "Improve (audit + targeted fixes)", "Replicate to another runtime"]` |
   | Detected stamp older than current plugin version | `upgrade` | `["Upgrade to current version (Recommended)", "Improve (audit + targeted fixes)", "Update (regenerate managed blocks)"]` |
   | Two+ runtimes | `improve` | `["Improve current setup (Recommended)", "Upgrade (apply version migrations)", "Replicate / sync between runtimes", "Update one runtime"]` |

3. Continue the interview — see [interview script](./references/interview.md). One question per `ask_user` call. Skip questions already answered by detection (project type, framework). After the Phase 0 mode choice, offer to use detected/safe defaults for non-gated setup questions. Never skip artifact tracking, MCP approval, plan approval, or security-sensitive write gates. For `init`/`update`, ask target runtimes only after mode if needed. For `improve`/`replicate`, jump straight to Phase 1.5; runtime expansion questions happen there only if required.

### Phase 1.5 — Improve / Upgrade / Replicate branch

If the user picked **improve** → run the [improve procedure](./references/replication.md#4-improve-mode-audit--targeted-upgrade) and [instruction-memory-audit](./references/instruction-memory-audit.md). Reuse existing memory, measure the entire file, inspect native adapters/overrides and skill discovery, then propose a compact replacement and relocation diff. User-authored content stays unchanged before approval; declined repair remains nonconforming. Misplaced artifacts are first-class deltas. Skip Phases 2–4; jump to Phase 5.

If the user picked **upgrade** → run the [version playbook](./references/misplaced-artifacts-migration.md#version-stamp-detection--migration-playbook) and [mismatch & deprecation detection](./references/misplaced-artifacts-migration.md#mismatch--deprecation-detection-upgrade-mode), then the instruction-memory audit. Classify historical deltas but target the current compact contract, not obsolete per-heading markers or full root matrices. Show `delete | add | patch | replace` groups; obtain approvals, capture preimages/backups, migrate workers/skills and their consumers before removing legacy artifacts, and record `prepared` → `applied` → `verified` in `.agents-system-setup/migration.jsonl`. Check structural drift even when version stamps match. Publish the manifest only after successful integration. Skip Phases 2–4; jump to Phase 5. Triggers include `agents-system-setup upgrade`, `/setup-copilot-agents upgrade`, and `$agents-system-setup upgrade`.

If the user picked **replicate** → run the [replication procedure](./references/replication.md#3-replication-procedure):
1. `ask_user` for **source** runtime (single-select among detected).
2. `ask_user` for **target** runtimes (multi-select; source excluded).
3. Parse source → AgentIR / SkillIR / MCPServerIR records.
4. Render lossiness report; `ask_user` to approve dropped fields per target.
5. Run **Phase 1.6** before any target write.
6. Re-run **Phase 3.5** MCP approval gate against each new target.
7. Emit per target with `<!-- agents-system-setup:replicated-from: <source> -->` markers.
8. Write replication ledger to `.agents-system-setup/replication.jsonl` (one JSON object per line — **never `.md`, never inside any `agents/` directory**, or it will be misread as a malformed agent).
9. Verify round-trip (re-parse emitted → diff IR → surface drift).

For **improve**, run Phase 1.6 before applying any selected delta. For both branches, finish with Phase 7 (verify & summarize).

### Phase 1.6 — Artifact Scope & Tracking

Run before Phase 1.7 for init/update, and before Phase 5 writes for improve/replicate. Use [local tracking](./references/local-tracking.md).

Ask:

> "Should the generated agent system be shared through git or kept local to this checkout?"
> Choices: `["Project files, git-tracked (Recommended for teams)", "Project files, local-only / untracked (Recommended for personal setup)", "Personal/global outside this repo"]`

Record `artifact_tracking` as `project-tracked | project-local | personal-global`.

Rules:
- `project-tracked`: use project paths; do not commit unless Phase 6 git actions are explicitly approved.
- `project-local`: use project paths, then add only generated/modified artifact paths to `.git/info/exclude` if `.git/` exists. Do not modify `.gitignore` for this.
- `personal-global`: use runtime user paths and avoid repo writes unless separately approved.

### Phase 1.7 — Domain Detection & Spec-Kit Recommendation

Run after Phase 1 (and 1.5 if branched), before Phase 2. Inspect the project brief gathered during interview against this software-development keyword set:

`app, application, api, service, microservice, library, sdk, cli, tool, devtool,
backend, frontend, fullstack, web, mobile, ios, android, desktop,
framework, plugin, extension, package, module,
infrastructure, infra, terraform, pulumi, kubernetes, helm,
compiler, parser, runtime, database, orm`.

If **any** keyword matches (case-insensitive, word-boundary), or the project already has source-language signals (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `*.csproj`, `pom.xml`, `Package.swift`, `build.gradle`, `mix.exs`, `composer.json`), classify as `software-dev`. Otherwise `non-dev` (marketing, research, content, data-analysis).

If `software-dev`, call `ask_user`:

> "This looks like a software project. Would you like to install **GitHub Spec-Kit** (Spec-Driven Development: `/specify` → `/plan` → `/tasks` → `/implement` slash commands) alongside the agent system?"
> Choices: `["Yes — install for this runtime (Recommended)", "Just print the install command", "No, skip"]`

On approval, emit the runtime-matched command from [spec-kit](./references/spec-kit.md) (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` then `specify init --here --ai <copilot|claude|codex|opencode>`). Print, never silently shell-out unless the user picked "install".

Record the choice in the plan so Phase 4 orchestrator output can reference the `/specify` workflow when appropriate.

### Phase 1.8 — Security, Audit, Architecture Intake

Run after domain detection and before Phase 2. Use [security-audit-architecture](./references/security-audit-architecture.md) as the source of truth.

Ask only questions not already answered by detection. Data sensitivity, auth
boundary, and external tools/MCP usage are mandatory. Infer audit evidence,
architecture style, critical qualities, and anti-pattern defaults into the plan
for low-risk projects unless the user asks to configure them explicitly.

Cover data sensitivity, auth, external tools/MCP, audit evidence, deployment/release
risk, architecture style, critical qualities and design anti-patterns per the reference.

Record the answers in the plan. If the user is unsure, choose safe defaults: least privilege, no silent MCP writes, no secrets in code, architecture decisions documented in `AGENTS.md`, and dedicated security/architecture ownership when the project handles sensitive data or external tools.

### Phase 1.8a — Security Team Scope

Run only for dedicated security team / bug-hunting setups; use [security team](./references/security-team.md). Record `security_team_depth`, `security_team_scope`, `authorization_scope`, selected roles, and source/vendor/license-attributed plugin candidates. Safe defaults: owned repo only, no external scanning/exploit execution/credential use/production testing/disclosure outreach/remediation writes without explicit approval; missing authorization returns `question_request`.

### Phase 1.9 — Output Profile & Context Budget + Advanced Agent Behavior

Run after Phase 1.8 and before Phase 2. Run the grouped
[interview Q9b Advanced agent behavior](./references/interview.md#9b-advanced-agent-behavior)
block explicitly; do not leave model or tool choices as prose-only plan notes.
Group agent-behavior choices together so the user compares tradeoffs once:
optional model overrides, Copilot CLI tool profile when Copilot is selected,
output profile, and Memory & Learning profile. This phase owns those prompts:
ask each advanced behavior choice exactly once and do not re-ask output profile
or memory profile in Phase 1.10. Use [context optimization](./references/context-optimization.md).

Ask and record the Q9b choices before Phase 2:

1. **Model selection policy** — record `adaptive-balanced` by default without another question. Ask about explicit overrides only on Q9b opt-in; preserve pins/providers/budgets and use actual runtime controls, not per-agent questionnaires.
2. **Copilot CLI Tool Profile** — only when Copilot CLI is selected; persist `copilot_tools_profile`. **Advisory supervision (Q9e)** is signal-gated and defaults to `advisory_supervision = off`: ask only when Copilot is selected, `parallel_safe_units >= 3`, and the user raised child sessions / parallel PRs / steering agents mid-run.
3. **Output profile / context budget** — `Balanced | Compact | Full`.
4. **Memory & Learning profile** — persist `learning_memory_profile`, `learning_gate_strength`, overwrite policy, and whether native provider memory is only documented or explicitly enabled.
5. **Build Gate (SDLC) strictness** — only when Phase 1.7 classified the project as `software-dev`; persist `build_gate_strictness` (`standard | strict | light | skipped`). See [sdlc-build-gate](./references/sdlc-build-gate.md). This single answer also seeds `code_quality_strictness` (no separate question; derive per [code-quality](./references/code-quality.md) — mirror the gate, floor to `light` when skipped, `advisory` for non-software-dev code-bearing projects, `n/a` when there is no source code).

For Copilot CLI tools, keep prompt choices concise: Standard least-privilege by
role (recommended), Read-only everywhere, Inherit parent tools, or Custom after
generation. Render the full mapping in the plan/reference, not in the question.

For the output profile choice, ask once:

> "How much detail should generated agent files include?"
> Choices: `["Balanced (Recommended)", "Compact", "Full"]`

Record:

- `output_profile`: `balanced | compact | full`
- `inline_sections`: which sections stay in `AGENTS.md`
- `overflow_targets`: approved local detail, normally `docs/agents/project-policy.md`
- `context_budget_notes`: any user constraints on verbosity

All profiles share the 150-line AND 12,288-byte root cap. Balanced is the default; Full expands on-demand material, not root memory. Keep critical control/owner/approval/gate triggers inline, with resolvable local detail.

### Phase 1.10 — Memory & Learning Profile

Do not call `ask_user` here. Use the Memory & Learning answer already collected
in the Phase 1.9/Q9b advanced-agent-behavior group. This phase normalizes the
recorded choice for planning and rendering. Use [learning memory](./references/learning-memory.md).

Record:
- `learning_memory_profile`: `project-tracked | project-local | personal-global | disabled`
- `native_learning_surface`: runtime-native memory selected or `document-only | disabled`
- `learning_memory_owner`: `@memory-steward` when the roster includes one, otherwise `@orchestrator`
- `learning_memory_path`: path chosen from [learning memory](./references/learning-memory.md#storage-profiles)
- `learning_gate_strength`: `recommended` by default; do not make it blocking unless the user explicitly asks
- `learning_update_policy`: `overwrite requires orchestrator approval`

Do not ask a separate blocking Learning Check question by default. Native memory
setup follows [learning memory](./references/learning-memory.md): Copilot Memory
is public-preview, transparent server-side durable repo memory, Claude has
`memory: user|project|local`, OpenCode relies on AGENTS/skills/compaction/plugin
patterns, Codex memories require `[features] memories = true`, and Gemini has
`save_memory`, `GEMINI.md`, `/memory`, and experimental `autoMemory`. Ask
optional hook/script support only when the runtime has a supported hook surface
and this setup has not already handled learning. Render the exact hook/config
proposal and ask before writing it.

### Phase 1.11 — Requirements Triage

Before Phase 2 planning, decide `requirements_triage_status`:

- `separate` — generate `requirements-triage` as its own read-mostly subagent.
- `merged` — host/planner owns triage without an extra worker.
- `skipped` — only when the task is direct, low-risk, single-runtime, and already has clear scope.

Default to `merged`; use `separate` when independent intake context is useful.
Resolve material ambiguity before work and retain scope, risk, acceptance,
quality gates, and `question_request`. The host owns decisions and approvals.

### Phase 1.12 — Content Quality Review

Before Phase 2 planning, decide `content_quality_curator`:

- `separate` — generate `agent-quality-curator` as its own read-only subagent.
- `merged` — host/reviewer owns prose review without an extra worker.
- `skipped` — only when no generated agent, skill, memory, recommendation, or output-contract prose is changed.

Default to `merged`; a separate read-only curator needs a task-based reason.
Use [content quality](./references/content-quality.md), preserve required
independence, and report `Content quality: ok|warn|fail|n/a; signals=<list|none>`.
Curators never own broad writes, configuration, release metadata, or approvals.

### Phase 2 — Plan (Directory Architecture, Roster, Matrix, Waves)

Build the plan and show it before writing anything. The plan must include:

- **Directory Architecture** — table of `path glob | purpose | owner agent | edit rule`. Derived from project type + frameworks. Always covers: source dirs, tests, docs, infra, agent files, generated artifacts.
- **Agent Roster** — table of `name | role | owns | triggers | model (optional) | parallel-safe | wave`. Use [topology guide](./references/topology.md). Compute parallel-safety per [parallelism](./references/parallelism.md): a subagent is parallel-safe iff its `owns` glob doesn't overlap any other's, it doesn't write outside `owns`, and it doesn't depend on another subagent's output in the same wave.
- **Capability Matrix** — capabilities × agents grid (✅ / 🟡).
- **Execution plan** — direct execution or justified waves with owners, dependencies, resource limits, and benefit over serial work; reconcile every dispatched result before dependent work.
- **Requirements triage** — status (`separate | merged | skipped`), intake brief, ambiguities, `question_request` count, risk flags, and recommended first-wave routing.
- **Content quality** — curator status (`separate | merged | skipped`), review scope, expected signals, and output marker from [content quality](./references/content-quality.md).
- **Security team operating model** — for `dedicated|expanded`, include roles, authorization scope, evidence contract, read-mostly defaults, and gates from [security team](./references/security-team.md).
- **Build Gate (SDLC)** — for enabled software-dev gates, include `max(size_bucket, criticality_bucket)`, matrix, evidence schema, and actual owners for every required responsibility. Do not force separate build-runner/change-bug-hunter/change-validator files. **Code Quality & Maintainability** — include strictness and conventions-first authoring standards; preserve independent review where required. Use [Build Gate](./references/sdlc-build-gate.md) and [code quality](./references/code-quality.md); record inapplicable concerns in the report.
- **Plan Handoff Contract** — accepted planning sources, HandoffIR fields, per-platform format targets, approval boundaries, and verification evidence. Use [handoff](./references/handoff.md).
- **Prompt assignment quality** — recommended handoff strictness, Orchestrator Assignment Format, Context Packet strategy, allowed capabilities, skills referenced, and expected `Task assignment quality` marker from [prompt guidelines](./references/prompt-guidelines.md).
- **Self-update preflight** — status, source path or provider manager, fast-forward evidence, and any `question_request` from [self-update preflight](./references/self-update-preflight.md).
- **Human Input protocol** — selected runtime matrix, native question tool or fallback, allowlist/config syntax, and unresolved `question_request` records from [human input](./references/human-input.md).
- **Skills to create** — for each candidate: `name`, trigger, `skill-kind` (`domain` for project knowledge), and the placement-rule justification. Derive candidates from `headline_purpose`, the Phase 1.7 domain classification, detected stack, Directory Architecture zones carrying non-obvious rules, and existing repo docs/ADRs — never a blank "what skills do you want?" prompt. Apply the four-part admission gate from [skill format](./references/skill-format.md#admission-gate-for-a-domain-skill) (project-specific, load-on-demand, stable trigger, not already covered); soft-cap ~1 per major ownership zone. The derived list is confirmed by this phase's existing approval gate — do not add a separate question.
- Plugin/MCP candidates **per capability** (Phase 3 fills this).
- Per-platform file plan, including native initializer requested/possible outputs, approved preimages, canonical memory, thin adapters, local policy, skill discovery paths, and any collision requiring review. See [native initialization](./references/native-initialization.md); Copilot defaults to the root-`AGENTS.md` request, asking only if unsupported/conflicting.
- **Artifact tracking** — `project-tracked | project-local | personal-global`, plus exclude plan for local-only mode.
- **Memory & Learning plan** — native-vs-plugin-managed memory choice, storage profile, memory owner, curated memory path, operational ledger path (if any), Learning Check strength, overwrite approval policy, and Directory Architecture rows for memory paths.
- Git actions (if any).
- **Output profile & context budget** — `balanced|compact|full`, whole-file 150-line/12,288-byte cap, local overflow targets, controlled adapter/import overhead, and unknown effective-context limits.
- **Security & Audit Matrix** — controls, owner agents, affected paths, evidence required, and source reference.
- **Threat Model Summary** — assets, trust boundaries, threats, mitigations, owners, and status.
- **Architecture & Design Pattern Matrix** — selected patterns, alternatives, rationale, risks/guardrails, and ADR refs.
- **ADR plan** — decisions that should become docs if the user approves docs writes.
- **Quality Gates** — build/test/lint/security/supply-chain/architecture evidence required before "done".

End the phase with `ask_user`: `["Proceed", "Edit plan first"]`.

### Phase 3 — Marketplace Lookup with per-item Opt-in

For every capability the user named (e.g., "playwright", "azure", "postgres"):

1. **Search** the marketplaces in tier order — see [marketplaces](./references/marketplaces.md). Tier 1 first; only fall through if it misses.
2. Collect **at most 3 candidates per capability**. For each, populate **mandatory rationale fields**: `name`, `source_tier`, `repo_url`, `bundles` (agents/skills/hooks/MCP/LSP), `why_recommended`, `tradeoffs`, `install_command_per_platform`. Empty rationale ⇒ drop the candidate.
3. Render a **comparison table** to the user, then call `ask_user`:
   > "For capability **<x>**, which would you like?"
   > Choices: `["<candidate 1 — short label>", "<candidate 2>", "<candidate 3>", "Show more (Tier-3 fallback search)", "None — skip this capability"]`
4. **Show more** triggers Tier-3 search (capped at +5 additional candidates). Re-render table and re-prompt.
5. Record the user's pick. Skipped capabilities never reach the MCP gate or final write.

See [plugin discovery](./references/plugin-discovery.md) for the comparison-table format and rationale schema.

For security-team setups, security plugins or skills remain optional candidates.
Show vendor/license attribution and tradeoffs. Never clone proprietary plugin
workflow text into generated agents, and never auto-install scanners, MCP
servers, or disclosure tooling.

### Phase 3.5 — MCP Config Approval Gate (mandatory, downstream of Phase 3)

If any user-selected candidate from Phase 3 includes an MCP server:

1. Build the proposed config **per platform**:
   - Copilot CLI → `.mcp.json` (`mcpServers` key) and any approved agent-frontmatter `mcp-servers:`
   - Claude Code → `.mcp.json` (`mcpServers` key) and any approved project/user-agent `mcpServers`
   - OpenCode → merge into `opencode.json` (`mcp` key)
   - OpenAI Codex → `.mcp.json` plus any approved per-agent TOML `[mcp_servers.<id>]`
   - Gemini CLI → approved per-agent `mcp_servers:` blocks in `.gemini/agents/*.md`
2. Render each proposed file/config block verbatim (full JSON/YAML/TOML as applicable).
3. For central MCP config files (`.mcp.json` and `opencode.json` with MCP
   blocks), include concrete approval evidence with server names:
   - Prefer a top-level `x-agents-system-setup` object when the runtime schema
     safely tolerates extension keys. Include `mcp_approval.decision`,
     `mcp_approval.servers`, `approved_by` or `approval_ref`, and `evidence`.
   - If extension keys are not schema-safe, write a sibling sidecar named
     `<config>.agents-system-setup.approval.json` with the same metadata.
4. `ask_user`:
   > "I'm about to write the MCP configuration above to `<paths>`. Approve?"
   > Choices: `["Approve all (Recommended)", "Approve selectively (per-server)", "Skip MCP entirely"]`
5. If **selective**, loop per server: `["Include", "Skip"]`.
6. If **skip**, strip every `mcp-servers:` / `mcpServers` / `mcp_servers:` / TOML `[mcp_servers.*]` surface from generated agents and do not write `.mcp.json` / `opencode.json` `mcp` / extension MCP config.
7. **No MCP write may occur before this gate returns approval.**

### Phase 4 — Generate Artifacts (per platform, post-approval)

First run [native initialization](./references/native-initialization.md) for the
active harness only, using approved paths/preimages; existing memory follows the
audit path instead. Copilot prefers `/init generate AGENTS.md at root instead of .github/copilot-instructions.md`;
ask only if unsupported/conflicting. Record actual output or disclosed fallback,
verify extracted repository facts, then synthesize once for all targets.

Render canonical/shared artifacts once and selected runtime artifacts using [platforms.md](./references/platforms.md) for paths and frontmatter:

- `AGENTS.md` → [synthesis template](./assets/AGENTS.md.template). Preserve native project facts and exact commands; keep Directory Architecture, justified roster, essential controls, architecture, Quality Gates and Skills index compact. Use [context optimization](./references/context-optimization.md) for root summary placeholders and optional Build Gate/Code Quality blocks. The complete merged file must pass 150 lines AND 12,288 UTF-8 bytes; never pad, truncate, or append a second manual.
- Local project policy → [template](./assets/project-policy.md.template), normally `docs/agents/project-policy.md`. Set `{{PROJECT_POLICY_PATH}}` in every consumer. Put full governance, Threat Model, ADR Index, Capability Matrix, Instruction Memory Audit, human-input and review detail here, not root lifecycle prose. Omit inapplicable sections and TOC entries; approved relocation must leave working local links.
- `GEMINI.md` when selected → [thin import template](./assets/GEMINI.md.template); honor configured context filenames. Claude uses its thin import adapter below. Copilot needs no additional `.github/copilot-instructions.md` when root memory suffices; preserve existing overrides and approve any adapter conversion.
- Orchestrator — **never emit as a subagent file** (subagent files are for specialized roles only). The orchestrator role lives in `AGENTS.md` › **Orchestration Operating Model** and is read by the host CLI session of any selected runtime. `@orchestrator` is a routing alias for that host session. OpenCode's `permission.task` subagent-gating moves to `opencode.json` › `agent.<root>.permission.task`. Improve / upgrade modes detect existing orchestrator subagent files and offer deletion/deprecation/manual-review choices via [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md#deprecated-orchestrator-subagent-files).
- Each subagent — use the **platform-specific template** and fill `{{OWNED_PATHS}}` / `{{READONLY_PATHS}}` from the Directory Architecture:
  - **Copilot CLI** → [subagent.agent.md.template](./assets/subagent.agent.md.template) at `.github/agents/<name>.agent.md`. Frontmatter: `name`, `description`, `tools:` list filled from the [Standard Tool Profile](./references/platforms.md#copilot-cli-standard-tool-profiles) per role (orchestrator + edit-capable subagents → `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors → `[read, search]`; testers/release helpers → `[execute, read, search, todo]`; research/docs → `[read, search, web, todo]`; or omit when the user picked `inherit`), optional `mcp-servers:` (hyphenated key). `.github/agents/<name>.md` is recognized only as an upstream docs-drift/import signal, not the default emitter.
  - **Claude Code** → [subagent.claude.md.template](./assets/subagent.claude.md.template) at `.claude/agents/<name>.md`. Frontmatter: `name`, `description`, optional `tools:` as **comma-separated string** (e.g. `Read, Grep, Bash`), optional `disallowedTools:`, `permissionMode:`, `model:`, etc. Do **not** use Copilot tool names or `mcp-servers:`.
  - **OpenCode** → [subagent.opencode.md.template](./assets/subagent.opencode.md.template) at `.opencode/agents/<name>.md`. Frontmatter: **no `name:`** (filename = agent name), `description`, `mode: subagent`, optional `model:` in `provider/model-id` format, optional `permission:` block. Do **not** embed `mcp-servers:` — MCP belongs in `opencode.json`.
  - **OpenAI Codex (CLI + App)** → [subagent.codex.toml.template](./assets/subagent.codex.toml.template) at `.codex/agents/<kebab-name>.toml`. Require `name`, `description`, `developer_instructions`; carry explicitly configured `tool_allowlist`, model and model-supported `model_reasoning_effort` strings without a closed effort enum. Use `sandbox_mode = "read-only"` for read-only roles. MCP tables require approval. Runtime config writes are separate proposals: preserve configured limits, use `agents.max_concurrent_threads_per_session` (`max_threads` is legacy), never invent six as a vendor default, and retain the non-recursive `max_depth = 1` safety policy unless explicitly changed. See [Codex layout](./references/platforms.md); CLI-only commands are usage notes, not App requirements.
  - **Gemini CLI** → [subagent.gemini.md.template](./assets/subagent.gemini.md.template) at `.gemini/agents/<kebab-name>.md`. Required fields: `name`, `description`; emit `kind: local`; optional `display_name`, `tools`, `mcp_servers`, `model`, `temperature`, `max_turns`, `timeout_mins`. Use snake_case `mcp_servers:` only after Phase 3.5 approval. Gemini subagents cannot call other subagents, so cross-agent work returns to the orchestrator/root session.
- Each skill → [template](./assets/skill.template.md) at a discoverable native location: Copilot `.github/skills/<name>/SKILL.md`; Claude `.claude/skills/<name>/SKILL.md`; OpenCode `.opencode/skills/<name>/SKILL.md`; Codex `.agents/skills/<name>/SKILL.md` or `~/.agents/skills/<name>/SKILL.md`; Gemini `.gemini/skills/<name>/SKILL.md`. Resolve overlapping discovery before copying; compatible runtimes may share one approved artifact. Root Skills rows state name, concrete trigger and native load/path. Legacy `.codex/skills` and operational-state misroutes go through [migration](./references/misplaced-artifacts-migration.md), never silent deletion.
- **`task-delegation` skill** — emit [template](./assets/task-delegation.skill.md.template) with `host-delegation` kind, discoverable in every target. Host load evidence `Skills Referenced: task-delegation loaded=true` must be true, but never implies child context. Pass required excerpts or use supported child loading. Workers retain inline fail-closed Acceptance Checklist + Reporting Template and never re-delegate.
- **Build Gate (SDLC)** — emit [code-change-build-gate](./assets/code-change-build-gate.skill.md.template) with its full local matrix/strictness/owner mapping, and `{{BUILD_GATE_ROOT_BLOCK}}` as the always-resident fail-closed trigger. Assign required responsibilities without forcing extra workers; keep required independent review. If skipped/non-dev, emit no gate skill/block and record rationale in the report. **Code Quality & Maintainability** — for code-bearing projects emit [code-quality](./assets/code-quality.skill.md.template), its authoring standards, and `{{CODE_QUALITY_ROOT_BLOCK}}`; preserve conventions-first behavior while writing. Pass true host load evidence plus actual child context, and retain `Code quality:` reporting. See [Build Gate](./references/sdlc-build-gate.md) and [code quality](./references/code-quality.md).
- MCP config (only if Phase 3.5 approved) at the platform's MCP path.
- Central MCP config files include the Phase 3.5 approval evidence either in top-level `x-agents-system-setup` metadata or in `<config>.agents-system-setup.approval.json`; generated configs with server names and no evidence are invalid.
- Per-agent MCP blocks include an `agents-system-setup:mcp-approved` marker from the Phase 3.5 decision; generated or improved agents with MCP blocks but no marker must be treated as unapproved until Phase 3.5 runs again.
- Resolve optional placeholders (`{{OPTIONAL_MCP_APPROVAL_MARKER}}`, `{{OPTIONAL_MCP_APPROVAL_COMMENT}}`, `{{OPTIONAL_PERMISSION_TASK_BLOCK}}`) using the [optional placeholder substitution table](./references/agent-format.md#optional-placeholder-substitution-table) before writing runtime agent directories. Generated runtime agents must contain no literal `{{OPTIONAL_...}}`; templates may keep placeholders.
- Drop the [directory-architecture snippet](./assets/directory-architecture.snippet.md) into any agent missing the boundary block.
- **Execution stance** — root Orchestration Operating Model allows direct work and justified dependency-aware waves. `task-delegation` holds the [parallelism](./references/parallelism.md) procedure; use concurrent calls only for worthwhile independent work and reconcile all dispatched results before dependent work.
- **Plan handoff contract** — preserve HandoffIR and the 12-field assignment schema in `task-delegation`, not root memory. Workers keep concise inline intake/output (Codex inside `developer_instructions`); use the [handoff](./references/handoff.md) and [prompt guidelines](./references/prompt-guidelines.md) contract without copying full plans.
- **Self-update preflight notes** — record Phase -1 status and approved update evidence in the report/operational state, not durable root memory. Do not imply MCP/plugin config changed outside its gated write path.
- **Human input protocol** — render the provider-specific question behavior from [human input](./references/human-input.md). Copilot agents never include `ask_user` in `tools:`; Claude restrictive allowlists include `AskUserQuestion` only for agents expected to ask; OpenCode uses nested `permission: { question: allow }`; Codex TOML has no human-input field and uses `question_request`; Gemini may allow `ask_user` for interactive agents.
- **Triage / content quality roles** — emit `requirements-triage` or `agent-quality-curator` only when justified as separate. Keep owner and responsibility in project policy; put current verdicts/evidence in the report. Both remain read-mostly/read-only and cannot grant approvals or write runtime/release configuration.
- **Security team operating model** — for `dedicated|expanded`, render `{{SECURITY_TEAM_OPERATING_MODEL}}`, selected roles, read-mostly defaults, and security evidence fields: authorization, validation, counterevidence, severity, remediation verification, and proof gaps.
- **Governance baseline** — keep critical control/owner/approval/gate summaries in root; render full security, audit, architecture, design-pattern and ADR detail in approved local project policy. Workers touching sensitive paths, MCP/tools, CI/release, dependencies or architecture retain explicit boundaries and audit evidence requirements.
- **Context optimization** — apply [context optimization](./references/context-optimization.md), its Task-Type Routing Map, and compact-mode trimming without losing gates. `Context freshness: recent` describes a host snapshot, not child inheritance; pass or load the child's required context. Codex follows the [summary + pointer rule](./references/agent-format.md#codex-toml-summary--pointer-rule).
- **Worker digest** — inline [project-standard digest](./assets/project-standard-digest.snippet.md) in every worker's managed hash block. Keep five required lines (three for Codex) and all inline safety guards; derive checks from actual project Quality Gates, never this plugin's CI commands. Audience tags are optional hints, not context exclusion; do not require per-heading markers or Self-Contained Notice prose in root.
- **Native Runtime Agents block** — when useful, render the short [snippet](./assets/host-builtins-routing.snippet.md) under Orchestration Operating Model, preserving `<!-- agents-system-setup:host-builtins-routing -->`; full runtime mechanics live in `task-delegation`, not Full-profile root memory. OpenCode built-in allows require its separate task gate, or record `host_builtins_routing: declined`. Routing stays host-only.
- **Tool catalog stamp & emit-time validation (v1.8.0+)** — emit `<!-- agents-system-setup:tool-catalog-version: {{PLUGIN_VERSION}} -->` in `AGENTS.md` and every generated agent immediately after the `generated-by` stamp. At emit time, consult [tool-catalog](./references/tool-catalog.md) for each runtime's `tools:` / `tool_allowlist` / `permission:` content; default-deny `scope: cli-only` and `scope: vscode-only` tools in shared `.github/agents/*.agent.md` files (opt-in must be recorded in the output contract). Emit the `tool-catalog-audit` skill at every selected runtime's skills path (Codex included) — host-side read-only audit. Do NOT add tool-catalog hints to subagent templates (hard rule #36).
- **`agents-doctor` health check (v1.9.0+)** — emit the [agents-doctor skill](./assets/agents-doctor.skill.md.template) at every selected runtime's skills path (Codex included) and render the read-only engine [agents-doctor.py.template](./assets/agents-doctor.py.template) to `.agents-system-setup/agents-doctor.py` (substitute `{{PLUGIN_VERSION}}` / `{{GENERATED_AT}}`). Record both in `.agents-system-setup/generated.json` (`kind: skill` and `kind: other`) so the doctor never flags its own files. Host-side read-only; subagents never invoke it (hard rule #36). It reconciles on-disk agents against the manifest and flags `stray-agent` / `orchestrator-subagent-file` / `missing-artifact` / `checksum-drift`. See [agents-doctor](./references/agents-doctor.md).
- **Memory & Learning System** — render the chosen profile from [learning memory](./references/learning-memory.md): `AGENTS.md` gets the native-vs-plugin-managed memory note, orchestrators get Reflect & Learn, subagents get Learning Check, and optional `assets/learnings.md.template` is emitted only when the memory profile needs a curated Markdown file. Sensitive new learnings require orchestrator and security-owner approval when tagged `risk` or when they mention MCP, CI/release, dependencies, secrets, or generated scripts. Do not write native memory config, hooks, or scripts unless separately approved.
- **OpenCode root-session task gate** — for OpenCode targets, render `permission.task` in `opencode.json` (under the host root agent, e.g. `agent.build.permission.task`) with `"*": deny` plus explicit roster-agent allows. This replaces the deleted `orchestrator.opencode.md` `permission.task` frontmatter; the host root session is the orchestrator. Treat this as a **separate config approval gate** (not the MCP gate): always propose the snippet when OpenCode is selected; if the user declines, record `opencode_task_gate: declined` and report `OpenCode task gate not installed; fan-out not permission-constrained` in the output contract. Broaden allows only when the plan says why.
- **OpenCode root-session skill gate** — propose `agent.<root>.permission.skill` in `opencode.json` with `"*": ask` and explicit named allows for emitted skills, including `task-delegation`. Preserve stricter existing policy. This is a separate config approval gate parallel to `permission.task`, not MCP approval. Decline records `opencode_skill_gate: declined`; retain worker inline guards, but report `Required skill load blocked` when loading is denied. Never fabricate `loaded=true`, silently allow both legacy/new names, or use wildcard allow for migration.
- **Artifact tracking** — apply [local tracking](./references/local-tracking.md). In `project-local` mode, update `.git/info/exclude` after writes and verify at least `AGENTS.md` with `git check-ignore -v`.
- **Spec-Kit** — if selected, put its workflow in on-demand project policy using [snippet](./assets/spec-kit-block.snippet.md); root keeps a concrete load trigger/link, not another lifecycle block. See [spec-kit](./references/spec-kit.md).
- **Claude Code AGENT-TEAMS.md** — when Claude Code is among the selected platforms AND the Agent Roster has 3+ subagents marked `team-suitable` (independent + benefits from peer challenge), emit `AGENT-TEAMS.md` documenting: opt-in env var (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), settings.json snippet, suggested teammate roster, token-cost warning, and when to fall back to parallel subagents.

**Project-memory adapters:** after canonical synthesis, use the skill's `scripts/link-project-memory.sh` or `.ps1` from the approved target directory to create a thin `CLAUDE.md` import. Helpers refuse existing nonidentical files/symlinks; approved replacements use Phase 5. Gemini uses its import template. No symlink/copy fallback or redundant Copilot file. Inspect actual imports/overrides and overlapping discovery per [cross-platform](./references/cross-platform.md).

**Frontmatter rules** (silent-failure traps):
- Formats with a `name` field (Copilot CLI, Claude Code, Gemini CLI, Codex TOML) MUST match filename basename (kebab-case); OpenCode Markdown agents MUST omit `name:` because the filename is the agent name.
- Quote any `description` containing colons.
- Subagent `description` MUST start with `"Use when..."`.
- Use the **right frontmatter schema per platform** (see [platforms.md](./references/platforms.md) — Copilot uses `mcp-servers:` and public tool aliases (`vscode`, `execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`), Claude uses comma-string `tools:`, OpenCode uses `mode:` plus `permission:`, Codex subagents use `.toml`, and Gemini uses `kind: local` plus `mcp_servers:`).
- Restrict tools per subagent to the minimum needed. For Copilot CLI, apply the Phase 4 Role → Profile mapping from [Copilot CLI Standard Tool Profiles](./references/platforms.md#copilot-cli-standard-tool-profiles) (Q9c override wins; default `Standard`).
- The `model:` line is optional in every platform — emit only if the user specified an override. When users opt in to overrides during interview Q9b, load [models](./references/models.md) for the runtime's accepted format, defaults, and rate-limit sources; never pin live RPM/TPM numbers in generated files.

### Phase 5 — Update Mode (non-destructive)

For each approved delta, preserve a non-overwriting `.bak`/ledger preimage,
parse the native format, and merge one managed block without losing user content.
Verify the live preimage before replacement; stop on concurrent edits, symlinks,
or destination collisions. Show retained rules and approved local relocations;
declined repairs stay nonconforming. Run the whole-file memory gate before
publishing the manifest. Update `.git/info/exclude` only for project-local
artifacts and print a concise diff summary. See [memory audit](./references/instruction-memory-audit.md).

### Phase 6 — Optional Git Init

Only if user confirmed in Phase 1 AND no `.git/` exists. Pick the script that matches the host OS — see [cross-platform](./references/cross-platform.md). The bundled scripts initialize `main`, write `.gitignore` and `.gitattributes`, stage, and commit.

### Phase 7 — Verify & Summarize

1. List every file created/modified with absolute paths, grouped by platform.
2. Re-read each generated agent/skill: confirm `name` matches filename for formats with a name field (Copilot, Claude Code, Gemini CLI, Codex TOML), no `name:` key in OpenCode files (filename is the name), `description` present and starts with `"Use when..."`, no unquoted colons, frontmatter parses for the *target platform's* schema. Confirm Claude Code `tools:` is a comma-separated string — not a YAML list. Confirm OpenCode files have no `mcp-servers:` key. Confirm Gemini files use `mcp_servers:` (not `mcpServers`) and do not instruct subagents to call subagents. Confirm no `agent: Plan` frontmatter was copied into any generated file.
3. Run `python3 .agents-system-setup/agents-doctor.py --memory-only --json` before final manifest publication. The entire root must pass <=150 physical lines AND <=12,288 UTF-8 bytes after substitution/merge, including user content. Hard failures block compliant completion; report exact counts and labeled/unavailable token measurements.
4. Confirm root ownership, justified roster, critical Security & Audit Matrix/Threat Model/Architecture & Design Pattern summaries, and Quality Gates. Full Capability Matrix and ADR Index belong in local project policy. Zero specialists is valid; no unresolved required owner, empty filler, broken local reference, or invented command.
5. Verify security-sensitive files (`.mcp.json`, `opencode.json`, `.env*`, CI/release config, lockfiles, generated scripts) have an owner and evidence requirement in the governance sections.
6. Confirm Context Loading Policy and Skills index contain concrete triggers plus discoverable native names/paths. Full Plan Handoff Contract and Task-Type Routing Map live in `task-delegation`/its local context; Instruction Memory Audit lives in project policy. Host-loaded evidence is not proof of child context or native loader success.
7. Verify the selected Memory & Learning System profile, owner/load path when enabled, no-secrets rule and overwrite approval. Workers propose Learning Check entries; disabled profiles produce no memory writes.
8. Verify every generated agent/subagent uses its target runtime's native handoff surface: Markdown body for Copilot/Claude/OpenCode/Gemini, TOML `developer_instructions` for Codex. Confirm each subagent template includes the **Assignment Intake / Preflight**, **Acceptance Checklist**, **Reporting Template**, and `Task assignment quality` marker; Codex TOML mirrors them inside `developer_instructions`. For Copilot CLI agents, confirm the `tools:` line matches the role's profile from [Copilot CLI Standard Tool Profiles](./references/platforms.md#copilot-cli-standard-tool-profiles): orchestrator + edit-capable subagents emit `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors emit `[read, search]`; the marker `<!-- agents-system-setup:tools-profile: <profile> -->` records the chosen profile.
9. Verify self-update preflight: the output records checked/current/fast-forwarded/requires-human/skipped status, and no MCP/plugin/runtime config changed outside the normal approval gates.
10. Verify human-input protocol: no Copilot `tools:` profile contains `ask_user`; Claude restrictive ask-capable agents include `AskUserQuestion`; OpenCode uses nested `permission` with `question`; Codex TOML has no `request_user_input` or `memory` field; Gemini interactive ask-capable agents may include `ask_user`; subagents document `question_request` fallback.
11. Verify content quality: project policy names the responsible host/reviewer/curator, workers report `Content quality`, and the final report records status/signals. Do not force a separate curator or persist transient task verdicts in root memory.
12. Verify artifact tracking: project-tracked files are visible to git; project-local files are ignored via `.git/info/exclude`; personal-global mode wrote no repo artifacts unless approved. Confirm no agents/skills/hooks/commands/prompts/plugins live under `.agents-system-setup/` — any detection from Phase 1 must have a `migration.jsonl` entry.
13. Print "Try it" examples per selected platform (`copilot`, `claude`, `opencode`, `codex`, `gemini`).
14. Suggest 2–3 next customizations.
15. Verify enabled Build Gate (SDLC) and Code Quality & Maintainability root triggers resolve to local `code-change-build-gate` / `code-quality` skills. The matrix, strictness and actual gate owners agree; missing skill/approval/evidence blocks work and sign-off. Required independent review remains independent, without forcing three gate workers. Retain `Build gate:` and `Code quality:` reporting; record skipped/non-applicable rationale in the report.
16. Verify `task-delegation` discovery, matching folder/frontmatter name, `host-delegation` kind, exact approved permissions, and renamed consumers. Legacy names remain only in explicit migration/history contexts. Workers retain the fail-closed inline guard and never re-delegate.
17. Verify worker self-containment: every emitted worker has the managed digest with five required lines (three for Codex), owned paths, acceptance, safety and reporting. Digest hash mismatch is WARNING, not ERROR. Do not demand root audience markers or infer unloaded context from a parent's snapshot.
18. Verify useful Native Runtime Agents routing uses the stable anchor and <=5-line root block in every profile, with full mechanics on demand. Workers never route other agents. OpenCode named built-ins require approved `permission.task` entries or an explicit declined status.
19. Verify Tool catalog discipline (#39): every generated agent and `AGENTS.md` carries the `<!-- agents-system-setup:tool-catalog-version: <plugin-version> -->` stamp marker; every `tools:` / `tool_allowlist` entry exists in the runtime's catalog block from `assets/tool-catalog.json`; OpenCode files have no deprecated `tools:` key (use `permission:`); no `scope: cli-only` / `scope: vscode-only` tools in shared `.github/agents/*.agent.md` unless explicitly opted in (recorded in the output contract). The `tool-catalog-audit` skill template exists at every selected runtime's skills path (Codex included).
20. Publish `.agents-system-setup/generated.json` only after successful integration; include native-init provenance, `memory_contract: native-compact-v1`, budget evidence, selected model policy and all artifact checksums. The `agents-doctor` skill and read-only engine are manifested; normal `python3 .agents-system-setup/agents-doctor.py` must reconcile clean. Missing manifests still exit 2 outside explicit `--memory-only`.
21. Inspect available native discovery/loading evidence, adapter/import overhead, applicable overrides and smaller configured budgets. File existence alone does not prove a running harness loaded it; report unavailable surfaces honestly and give runtime-correct reload/new-session guidance.

### Phase 8 — Final Wrap-Up (single consolidated ask)

Run after Phase 7, **before** exiting. Present one compact multi-select menu from [wrap-up](./references/wrapup.md), filtered by domain/plugins/MCP/platform signals. Never show installed items; never ask one item at a time. Re-confirm only if an action edits config outside `AGENTS.md`. Skip the entire phase only when `mode == update` and no agents/plugins/MCP changed.

## Anti-patterns

- **Approval-gate skips.** Never write files before showing the plan; never write MCP config without explicit `ask_user` approval; never bulk-apply recommendations without per-item rationale + choice.
- **Agent identity & naming hygiene.** Don't mix platform frontmatters (e.g., Copilot keys in a Claude agent file); don't write generic descriptions ("helps with code") that kill discovery; don't invent plugin/skill/MCP names — always cite `[Tier · Vendor]` from [marketplaces](./references/marketplaces.md).
- **Pairwise replication code** (Copilot→Claude function, Claude→OpenCode function, …) — always go through the [Canonical IR](./references/replication.md).
- **Replication / update safety lapses.** Don't replicate without re-triggering the MCP approval gate for the new target(s); don't overwrite existing `AGENTS.md` / `opencode.json` without `.bak`.
- **Cross-OS slips on generated files** — use thin native import adapters, not symlink/copy fallbacks; preserve existing files until approved migration. Use forward slashes and `.gitattributes` so shell files retain LF.
- **Unjustified topology.** Don't create workers to satisfy a count or force fan-out for small/sequential work. Direct execution never bypasses ownership, independent review, or other required gates; see [parallelism](./references/parallelism.md).
- **Mishandling Codex/Gemini subagent contracts.** Codex subagents live at `.codex/agents/<name>.toml` and MUST have `name`, `description`, and `developer_instructions` (missing any = silent skip on load); reserve `## <Name>` headings in `AGENTS.md` for orchestrator + project rules. Gemini local subagents at `.gemini/agents/*.md` cannot recursively delegate (fan-out routes through the parent session) and must use loader-valid `mcp_servers:` (snake_case), not the docs-spelled `mcpServers`. Both still pass the MCP approval gate. See [openai docs](https://developers.openai.com/codex/subagents).
- **Wrap-up hygiene failures.** Skipping Phase 8 denies users the curated add-on menu; the wrap-up must be a *single* multi-select prompt (not per-item round-robin); only cite vendor-official docs or the catalogs listed in [wrap-up](./references/wrapup.md).
- **Wrong directory for operational logs / runtime artifacts.** Operational logs (replication, migration, MCP approval evidence) belong in `.agents-system-setup/*.jsonl` — never `.md` and never inside any `agents/` tree (the runtime loader parses them as malformed agents). Writing runtime artifacts under `.agents-system-setup/` (agents, skills, hooks, commands, prompts, plugins) is silently inert; use per-platform paths from Phase 4. See [replication](./references/replication.md#5-anti-patterns) and [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md).
- **Running deep recon before knowing user purpose** — anchors the interview on what the directory looks like instead of what the user wants. Phase 0 sub-step 0 captures `headline_purpose` first; Phase 1 recon scores against that intent. See hard rule #32 and [cwd-reconnaissance](./references/cwd-reconnaissance.md#purpose-aware-scoring).
- **Emitting an `orchestrator` subagent file** — `@orchestrator` is the host CLI session reading `AGENTS.md`, not a runtime artifact. A delegated `orchestrator` subagent often does the work itself instead of fanning out to specialists (subagent runtimes give it the same broad toolset). Codex CLI has never emitted an orchestrator TOML; v1.3.0 normalizes Copilot/Claude/OpenCode/Gemini to that pattern and moves OpenCode `permission.task` to `opencode.json`. See hard rule #33 and [misplaced-artifacts-migration](./references/misplaced-artifacts-migration.md#deprecated-orchestrator-subagent-files).
- **Governance treated as optional.** Security/architecture baselines are part of planning and generation (not a wrap-up postscript); every architecture/design-pattern decision needs alternatives, guardrails, and an ADR reference (or `n/a` rationale); security review is read-mostly unless the plan grants tightly scoped remediation paths.
- **Content-quality and artifact-tracking slips.** Content-quality review must remove generic/unsupported/repetitive prose, keep generated subagent prose lean (no long quality rules pasted everywhere), and link moved overflow detail from `AGENTS.md` or the output contract; always ask the tracking mode before writing project files; local-only project agents go in `.git/info/exclude`, never `.gitignore`.
- **Frontmatter-schema confusion.** Don't copy VS Code `plan` prompt frontmatter (`agent: Plan`) into agent files — normalize to HandoffIR, then emit per-platform; don't put human-input tools in the wrong schema (no Copilot `ask_user` in custom-agent `tools:`, no literal OpenCode `permission.question`, no Codex TOML `request_user_input`, no unsupported memory fields).
- **Silent self-updates that change config** — Phase -1 may fast-forward the skill checkout only; plugin/MCP/runtime config changes still need their normal approval gates.

## Output Contract

Use [output-contract](./references/output-contract.md): include Update preflight, Human input, native initialization provenance, Context profile/split, exact whole-file memory sizes, compliance/repair status, and actual skill-loading evidence. Lead with the outcome; distinguish source-backed defaults, requested behavior and observed runtime results.
