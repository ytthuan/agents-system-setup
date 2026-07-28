# Interview Script

Use the provider-native human-input tool for **every** question (Copilot CLI uses session `ask_user`; see [human input](./human-input.md)). One question per call. Multiple-choice when possible (the runtime adds a freeform option automatically — never include "Other" in choices).

## 0. Opening (purpose first, then mode/platforms)

### 0a. Capture headline purpose

Before any directory scan or mode choice:

- Q: "In one sentence, what are you trying to achieve with an agent system here?"
- Freeform.
- Offer the labeled alternative `"I'm exploring — let recon lead"` so
  users without a clear intent can defer the purpose ask until after
  the Phase 1 recon card has been rendered.
- **Normalization rule:** record `headline_purpose = "exploring"`
  **only** when the user selects that exact labeled choice. Vague
  freeform answers (`"not sure"`, `"whatever"`, blank, short impatient
  strings) are stored verbatim as weak headlines, not promoted to the
  `exploring` sentinel.
- Record `headline_purpose: string | "exploring"`. Phase 1 recon uses
  this to score and rank signals — see
  [cwd reconnaissance / Purpose-aware scoring](./cwd-reconnaissance.md#purpose-aware-scoring).

### 0b. Detect footprint, then ask mode

Show a compact profile card: detected project type, existing agent
artifacts, the captured `headline_purpose`, recommended mode, and
inferred target runtime(s).

- Q: "I detected `<footprint>`. How should I proceed?"
- Choices: `["Improve current setup (Recommended when artifacts exist)", "Init new setup", "Replicate / sync to another runtime", "Update managed blocks", "Cancel"]`
- Then ask target runtimes only when the mode needs them:
  `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex only (CLI + App artifacts)", "Gemini CLI only", "Copilot CLI + Claude Code", "All supported runtimes (Copilot + Claude Code + OpenCode + Codex + Gemini)"]`

## 1. Purpose (confirm or revisit)

- When `headline_purpose` is a real headline:
  - Q: "Earlier you said: `<headline>`. Anything to add or correct?"
  - Freeform. Accept blank to confirm.
- When `headline_purpose == "exploring"`:
  - Skip this question until after the Phase 1 cwd reconnaissance card
    has been confirmed, then re-ask the original Q0a as a fresh
    purpose ask: "Now that you've seen the project, what are you
    trying to achieve?"
- **Recon pre-fill / enrichment:** the Phase 1 cwd reconnaissance card
  may surface a `docs_signals.summary` the user can incorporate; never
  auto-replace the confirmed headline.

## 2. Mode follow-up
- Q0b is the mode decision. Do not ask a second mode question during the normal
  flow.
- Re-prompt only when detection or the initial answer is ambiguous, using the
  full Q0b choice set:
  `["Improve current setup (Recommended when artifacts exist)", "Init new setup", "Replicate / sync to another runtime", "Update managed blocks", "Cancel"]`
- Never offer overwrite. If the user wants a fresh setup near existing
  artifacts, treat it as additive init or route through update/improve.

## 3. Project Type
- Q: "What type of project is this?"
- Choices: `["Documentation site", "Web — .NET", "Web — Node.js/TypeScript", "Web — Python", "Web — Go", "Web — Other", "iOS app", "Android app", "CLI tool", "Library / SDK", "Monorepo", "Data / ML", "Infrastructure / DevOps", "Security team / Bug hunting"]`
- **Recon pre-fill:** when the Phase 1 cwd reconnaissance card has
  `project_kind_signals`, sort or highlight the matching choices first
  (for example `data_signals` lifts `Data / ML`, `infra_signals` lifts
  `Infrastructure / DevOps`). The user always confirms — never auto-pick.

After showing detected purpose/type/language/test/deploy values, offer a fast
path for non-gated questions:

- Q: "Use detected and safe defaults for remaining non-gated setup questions?"
- Choices: `["Yes — use detected/safe defaults (Recommended)", "No — ask each setup question"]`
- This shortcut must not skip artifact tracking, MCP approval, plan approval,
  or security-sensitive write gates.

## 4. Languages
- Q: "Primary language(s)? (comma-separated)"
- Freeform.

## 5. Frameworks & Runtimes
- Q: "Key frameworks, runtimes, and major dependencies?"
- Freeform.

## 6. Testing
- Q: "Test framework in use (or planned)?"
- Freeform. Allow `none`.

## 7. Deployment Target
- Q: "Where does this ship?"
- Choices: `["Cloud (Azure)", "Cloud (AWS)", "Cloud (GCP)", "Container registry", "npm / PyPI / NuGet / Crates", "App Store / Play Store", "Static host (Pages/Netlify/Vercel)", "Internal / N/A"]`

## 8. Customization Scope
- Q: "Should the generated agent system be shared through git or kept local to this checkout?"
- Choices: `["Project files, git-tracked (Recommended for teams)", "Project files, local-only / untracked (Recommended for personal setup)", "Personal/global outside this repo"]`
- Record as `artifact_tracking`: `project-tracked`, `project-local`, or `personal-global`.

## 9. Subagent Topology
- Show the suggestion derived from project type via [topology.md](./topology.md).
- Q: "Suggested subagents: <list>. Accept, add, or remove?"
- Freeform with the suggested list pre-printed.

## 9a. Security team depth (only when requested or selected)

Ask this only when Q3 is `Security team / Bug hunting`, or when the user brief
mentions bug hunting, vulnerability research, appsec review, security analysis,
disclosure triage, bug bounty, exploitability, threat modeling, or remediation
verification.

- Q: "How deep should the generated security team be?"
- Choices: `["Baseline security auditor only", "Dedicated bug-hunting/security analysis team (Recommended)", "Expanded AppSec program with disclosure/supply-chain/cloud/compliance options"]`
- Record as `security_team_depth`: `baseline | dedicated | expanded`.

If `dedicated` or `expanded`, load [security team](./security-team.md) for role
sizing and safe authorization boundaries. Do not auto-enable external scanning,
exploit execution, disclosure outreach, MCP servers, or security plugins from
this answer alone.

## 9d. SDLC Build Gate (only when software-dev)

Ask this only when Phase 1.7 classified the project as `software-dev` (the
project brief or detected language signals matched the software-dev keyword
set). Skip for documentation sites, security-team-only setups, research, or
content projects.

- Q: "Enable the SDLC Build Gate for code changes? It runs build, unit test,
  e2e test, code review, change-scoped bug hunt, and final validation; gates
  scale with the diff size and critical surfaces touched."
- Choices: `["Standard (Recommended)", "Strict (promote recommended gates to required; XL needs two reviewers + release-validator)", "Light (merge change-validator into reviewer; XS=build+review only)", "Skip"]`
- Record as `build_gate_strictness`: `standard | strict | light | skipped`.

If `skipped`, the plugin renders `Build Gate (SDLC): n/a — user skipped` in
`AGENTS.md` and does not emit `build-runner`, `change-bug-hunter`,
`change-validator`, the `code-change-build-gate` skill, or the matrix
snippet. If `standard|strict|light`, the plugin emits the Build Gate per
[sdlc-build-gate.md](./sdlc-build-gate.md). Default is `standard` when the
user accepts the recommendation.

This single answer also seeds **`code_quality_strictness`** — there is no second
strictness question. Code quality is the *authoring* craft (conventions,
maintainability) applied while writing; the Build Gate is *verification*. Derive
per [code-quality.md](./code-quality.md): `standard|strict|light` mirrors
`build_gate_strictness`; `skipped` build gate floors code quality to `light`
(standards still apply, merged into `@reviewer`) unless the user explicitly opts
out of code quality; a non-software-dev but code-bearing project (scripts, IaC,
config, notebooks) gets `advisory`; a project with no source code gets `n/a`.

## 9b. Advanced agent behavior

Ask these choices together after topology so users compare the tradeoffs in one
place. Skip runtime-specific questions when that runtime is not selected. **By
default, do not ask the Per-Agent Model Override policy** — assume `model:` lines
are omitted everywhere unless the user opts in (see below).

### Per-Agent Model Override policy (optional opt-in only)

**Default: skip this question entirely.** Record
`model_overrides_policy = skipped` and emit no `model:` lines in any generated
agent. Platform defaults are intentional: they avoid rate-limit fragility,
preserve portability, and let users upgrade models without regenerating.

Ask the opt-in question only when **at least one** signal indicates the user is
aware of and wants model overrides:

- The user spontaneously named a model (e.g. "use Sonnet 4.5", "gpt-5-mini",
  "haiku for review agents") in the brief, prior turns, or any earlier
  interview answer.
- The user explicitly asked for model overrides, BYOK, multi-model routing,
  cost/perf tuning, or per-role model selection.
- The user picked a runtime where model selection is unusually impactful
  (e.g. they mentioned BYOK on Copilot CLI) and asked about tuning.

When any signal is present, ask the meta gate first:

- Q: "You mentioned models — want to configure per-agent model overrides? Most
  setups should skip and use platform defaults."
- Choices: `["Skip — use platform defaults (Recommended)", "Yes — show me override options"]`
- On `Skip`, record `model_overrides_policy = skipped` and stop.
- On `Yes`, then ask the scope question below.

Scope question (only after the user opts in):

- Q: "How should agent model overrides work? Defaults avoid rate-limit and portability issues."
- Choices: `["One model for all agents", "By role/profile", "Exceptions only"]`
- Load [models](./models.md) and prompt only for the chosen scope. Do not loop
  over every agent unless the user explicitly picks per-agent exceptions. Warn
  when a supplied id does not match the documented runtime format.

If the question was not asked, the wrap-up phase may surface model overrides as
an optional add-on — never as a required step.

### 9c. Copilot CLI Tool Profile (only if Copilot CLI is selected)

- Q: "How should I set Copilot CLI `tools:` allowlists?"
- Choices: `["Standard least-privilege by role (Recommended)", "Read-only everywhere", "Inherit parent tools", "Custom after generation"]`
- Default: `Standard profile` / `Standard least-privilege by role`. Persist as `copilot_tools_profile`. The detailed mapping lives in the plan and [Copilot CLI Standard Tool Profiles](./platforms.md#copilot-cli-standard-tool-profiles): orchestrator/edit-capable agents get `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors get `[read, search]`; runner/research profiles stay narrow.

### 9e. Advisory supervision of child sessions (signal-gated, off by default)

**Default: skip this question entirely.** Record `advisory_supervision = off`.
Cross-session supervision only exists in the GitHub Copilot app, and the standard
wave model already covers the common case.

Ask **only when all three** signals hold:

1. Copilot CLI / app is a selected runtime.
2. `parallel_safe_units >= 3` — see the sizing floor in
   [supervising a running child session](./parallelism.md#supervising-a-running-child-session);
   below three units the cross-session integration overhead outweighs the benefit.
3. The user mentioned child sessions, parallel PRs, `/orchestrate`, or steering
   agents while they run.

One question, no follow-up:

- Q: "Should the host supervise child sessions while they run, or just dispatch and integrate?"
- Choices: `["Off — dispatch and integrate (Recommended)", "Plan gate only", "Standard — plan gate plus premise steering"]`
- Record as `advisory_supervision` (`off` | `plan-gate` | `standard`). See
  [parallelism](./parallelism.md#supervising-a-running-child-session) for the
  checkpoints, the polling ban, and the wave-close reconciliation invariant.

If the question was not asked, Phase 8 wrap-up may surface it as an optional
add-on — never as a required step.

### Output profile / context budget

- Q: "How much detail should generated agent files include?"
- Choices: `["Balanced (Recommended)", "Compact", "Full"]`
- Record as `output_profile`. If the user is unsure, choose `Balanced`.

### 11i. Memory & Learning profile

- Q: "How should generated agents store durable learnings from past work?"
- Choices: `["Project-tracked curated memory (Recommended for teams)", "Project-local / untracked memory (Recommended for personal setup)", "Personal/global memory outside this repo", "Disabled"]`
- Record as `learning_memory_profile` and `native_learning_surface = document-only` unless the user explicitly asks to enable a provider-native memory feature.
- Do not ask a separate blocking Learning Check question by default. Record `learning_gate_strength = recommended` and `learning_update_policy = overwrite requires orchestrator approval`. Only make Learning Check blocking when the user explicitly requests it.
- Native memory options are provider-specific; use [learning memory](./learning-memory.md) and never emit unsupported fields such as Codex agent TOML `memory`.

## 10. Plugin / Skill / MCP Discovery Scope
- Q: "Which capabilities should I look up in the marketplaces (github/awesome-copilot, github/copilot-plugins, anthropics/skills, openai/skills, OpenCode catalogs, Gemini extensions)? (comma-separated, e.g., 'playwright, azure, postgres')"
- Freeform. Allow `skip`.
- If the Phase 1.8 external-tools answer has already been recorded as `No external tools`, default this to `skip` and do not enter Phase 3 unless the user explicitly adds capabilities.
- If the external-tools answer is not available yet, derive likely capabilities from the detected stack, ask the user to confirm or edit the list, and later keep it skipped if the security intake confirms `No external tools` without explicit capabilities.

> **This question is about skills to *install*, not skills to *author*.** Project
> domain skills (`skill-kind: domain` — business rules, regulatory constraints,
> this repo's coordination conventions) are **not asked for here and never
> elicited by a blank prompt.** They are derived in Phase 2 from
> `headline_purpose`, the Phase 1.7 domain classification, the detected stack,
> Directory Architecture zones carrying non-obvious rules, and existing repo
> docs/ADRs, then confirmed by Phase 2's existing plan-approval gate — the same
> way the Directory Architecture and Agent Roster are confirmed. No extra
> question. See the admission gate in
> [skill format](./skill-format.md#admission-gate-for-a-domain-skill) and the
> [placement rule](./context-optimization.md#2a-placement-rule--where-a-piece-of-knowledge-goes).

## 10b. MCP Approval Mode (only if any MCP server is among selections later)
- Q: "How should I handle MCP server config writes when we get to the approval gate?"
- Choices: `["Approve all at once after I show the config (Recommended)", "Approve selectively, per server", "Skip MCP entirely — recommend in plan only, write nothing"]`

## 11. Security, Audit, Architecture Intake

Use [security-audit-architecture](./security-audit-architecture.md). Ask only questions not answered by detection, one `ask_user` call at a time.

### 11a. Data sensitivity
- Q: "What is the highest sensitivity of data this project handles?"
- Choices: `["Public only", "Internal business data", "User personal data / PII", "Payment / financial data", "Health / regulated data", "Secrets or credentials"]`

### 11b. Auth boundary
- Q: "How is access controlled?"
- Choices: `["No auth", "User login", "Service-to-service auth", "OAuth/OIDC", "API keys", "Unsure"]`

### 11c. External tools / MCP
- Q: "Will agents call external systems or MCP servers?"
- Choices: `["No external tools", "Approved internal tools only", "Public APIs", "MCP servers", "Unsure"]`

### 11d. Audit evidence (infer unless risk requires asking)
- Q: "What audit evidence should agents preserve?"
- Choices: `["Diff summary only", "Test/build evidence", "Security findings", "Decision records / ADRs", "Compliance evidence", "Unsure"]`

### 11e. Architecture style (infer unless ambiguous)
- Q: "What architecture style should the agents preserve or move toward?"
- Choices: `["Layered", "Clean/Hexagonal", "Event-driven", "Microservices", "Modular monolith", "Serverless", "CLI/library", "Unsure"]`

### 11f. Critical qualities (infer safe defaults, then show in plan)
- Q: "Which quality attributes matter most?"
- Choices: `["Security", "Reliability", "Maintainability", "Performance", "Cost", "Accessibility", "Compliance"]`

### 11g. Design anti-patterns
- Q: "Any architecture or design anti-patterns to avoid?"
- Freeform. Allow blank.

Ask 11d-11g only when the profile card indicates sensitive data, auth, MCP,
release/deploy risk, regulated context, or when the user declined safe defaults.
Otherwise infer conservative defaults into the plan and let the user edit before
writes. If hooks/scripts are requested, show the exact runtime-specific
hook/config proposal and ask before writing.

## 12. Git
- Only if no `.git/` present.
- Q: "No git repo detected. Run `git init` + `.gitignore` + initial commit?"
- Choices: `["Yes (Recommended)", "No, leave git untouched"]`

## 13. Plan Approval (after Phase 2)
- Q: "Here is the plan: <render>. Proceed?"
- Choices: `["Yes, proceed", "Edit plan first"]`

## 14. Per-Capability Recommendation Choice (Phase 3, looped)
- One call per capability the user named in Q10.
- Q: "For capability **<x>**, which would you like?"
- Choices built dynamically: `["<candidate 1 — name + tier>", "<candidate 2>", "<candidate 3>", "Show more (Tier-3 fallback)", "None — skip this capability"]`
