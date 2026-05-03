# Interview Script

Use `ask_user` for **every** question. One question per call. Multiple-choice when possible (the runtime adds a freeform option automatically — never include "Other" in choices).

## 0. Opening prompt (detect first, then choose mode/platforms)

- Detect the current footprint before asking. Show a compact profile card:
  detected project type, existing agent artifacts, recommended mode, and inferred
  target runtime(s).
- Q: "I detected `<footprint>`. How should I proceed?"
- Choices: `["Improve current setup (Recommended when artifacts exist)", "Init new setup", "Replicate / sync to another runtime", "Update managed blocks", "Cancel"]`
- Then ask target runtimes only when the mode needs them:
  `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex only (CLI + App artifacts)", "Gemini CLI only", "Copilot CLI + Claude Code", "All supported runtimes (Copilot + Claude Code + OpenCode + Codex + Gemini)"]`

## 1. Purpose
- Q: "In one sentence, what does this project do?"
- Freeform.

## 2. Mode follow-up
- Q0 is the mode decision. Do not ask a second mode question during the normal
  flow.
- Re-prompt only when detection or the initial answer is ambiguous, using the
  full Q0 choice set:
  `["Improve current setup (Recommended when artifacts exist)", "Init new setup", "Replicate / sync to another runtime", "Update managed blocks", "Cancel"]`
- Never offer overwrite. If the user wants a fresh setup near existing
  artifacts, treat it as additive init or route through update/improve.

## 3. Project Type
- Q: "What type of project is this?"
- Choices: `["Documentation site", "Web — .NET", "Web — Node.js/TypeScript", "Web — Python", "Web — Go", "Web — Other", "iOS app", "Android app", "CLI tool", "Library / SDK", "Monorepo", "Data / ML", "Infrastructure / DevOps"]`

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

## 9b. Advanced agent behavior

Ask these choices together after topology so users compare the tradeoffs in one
place. Skip runtime-specific questions when that runtime is not selected.

### Per-Agent Model Override policy (optional)

- Q: "How should agent model overrides work? Defaults avoid rate-limit and portability issues."
- Choices: `["No overrides — use platform defaults (Recommended)", "One model for all agents", "By role/profile", "Exceptions only"]`
- If not `No overrides`, load [models](./models.md) and prompt only for the chosen scope. Do not loop over every agent unless the user explicitly picks per-agent exceptions. Warn when a supplied id does not match the documented runtime format.

### 9c. Copilot CLI Tool Profile (only if Copilot CLI is selected)

- Q: "How should I set Copilot CLI `tools:` allowlists?"
- Choices: `["Standard least-privilege by role (Recommended)", "Read-only everywhere", "Inherit parent tools", "Custom after generation"]`
- Default: `Standard profile` / `Standard least-privilege by role`. Persist as `copilot_tools_profile`. The detailed mapping lives in the plan and [Copilot CLI Standard Tool Profiles](./platforms.md#copilot-cli-standard-tool-profiles): orchestrator/edit-capable agents get `[vscode, execute, read, agent, edit, search, todo]`; reviewers/auditors get `[read, search]`; runner/research profiles stay narrow.

### Output profile / context budget

- Q: "How much detail should generated agent files include?"
- Choices: `["Balanced (Recommended)", "Compact", "Full"]`
- Record as `output_profile`. If the user is unsure, choose `Balanced`.

### 11i. Memory & Learning profile

- Q: "How should generated agents store durable learnings from past work?"
- Choices: `["Project-tracked curated memory (Recommended for teams)", "Project-local / untracked memory (Recommended for personal setup)", "Personal/global memory outside this repo", "Disabled"]`
- Record as `learning_memory_profile`.
- Do not ask a separate blocking Learning Check question by default. Record `learning_gate_strength = recommended` and `learning_update_policy = overwrite requires orchestrator approval`. Only make Learning Check blocking when the user explicitly requests it.

## 10. Plugin / Skill / MCP Discovery Scope
- Q: "Which capabilities should I look up in the marketplaces (github/awesome-copilot, github/copilot-plugins, anthropics/skills, openai/skills, OpenCode catalogs, Gemini extensions)? (comma-separated, e.g., 'playwright, azure, postgres')"
- Freeform. Allow `skip`.
- If the Phase 1.8 external-tools answer has already been recorded as `No external tools`, default this to `skip` and do not enter Phase 3 unless the user explicitly adds capabilities.
- If the external-tools answer is not available yet, derive likely capabilities from the detected stack, ask the user to confirm or edit the list, and later keep it skipped if the security intake confirms `No external tools` without explicit capabilities.

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
