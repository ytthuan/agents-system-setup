# Interview Script

Use `ask_user` for **every** question. One question per call. Multiple-choice when possible (the runtime adds a freeform option automatically — never include "Other" in choices).

## 0. Platform Selection (FIRST question after detection)
- Q: "Which agent runtime(s) should I configure?"
- Choices: `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "OpenAI Codex only (CLI + App artifacts)", "Gemini CLI only", "Copilot CLI + Claude Code", "All supported runtimes (Copilot + Claude Code + OpenCode + Codex + Gemini)"]`

## 1. Purpose
- Q: "In one sentence, what does this project do?"
- Freeform.

## 2. Mode
- Detect first. Ask only if ambiguous:
- Q: "I detected `<existing files>`. Should I run in **init** or **update** mode?"
- Choices: `["update (Recommended)", "init (overwrite existing as new setup)"]`

## 3. Project Type
- Q: "What type of project is this?"
- Choices: `["Documentation site", "Web — .NET", "Web — Node.js/TypeScript", "Web — Python", "Web — Go", "Web — Other", "iOS app", "Android app", "CLI tool", "Library / SDK", "Monorepo", "Data / ML", "Infrastructure / DevOps"]`

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

## 9b. Per-Agent Model Override (optional, ask only if user wants to set models)
- Q: "Want to set a custom model for any agent? Each runtime has its own accepted format and plan-tier rate limits — see [models](./models.md). Leave blank to keep the runtime's default and stay portable."
- Choices: `["No, use platform default for all (Recommended)", "Yes, I'll specify per agent"]`
- If yes: loop per agent. Before each prompt, surface the runtime's accepted format from [models.md](./models.md) (Copilot internal id, Claude alias or full id, OpenCode `provider/model-id`, Codex `gpt-5.x` plus optional `model_reasoning_effort`, Gemini local id). Freeform input; `inherit` or blank skips that agent. Warn when the supplied id does not match the documented format and ask whether to keep it.

## 9c. Copilot CLI Tool Profile (only if Copilot CLI is among selected runtimes)
- Q: "How should I set the `tools:` allowlist for Copilot CLI agents? See [Copilot CLI Standard Tool Profiles](./platforms.md#copilot-cli-standard-tool-profiles) for the full mapping."
- Choices: `["Standard profile (Recommended) — [vscode, execute, read, agent, edit, search, todo] for orchestrator/implementer; [read, search] for reviewers/auditors; runner/research profile for testers/docs gatherers", "Minimal — emit only the read-only profile [read, search] everywhere; require explicit per-agent opt-in for execute/edit/agent", "Custom — I will edit per-agent after generation; emit no default", "Inherit — omit tools: line; agents inherit all parent tools"]`
- Default: `Standard profile`. Persist as `copilot_tools_profile`. The renderer applies the role → profile mapping in Phase 4 unless the user picked `Custom` or `Inherit`. `Minimal` overrides every role to `read-only`. `Custom` leaves `tools:` blank in subagents but still emits the standard line on the orchestrator (the orchestrator needs `agent` to delegate).

## 10. Plugin / Skill / MCP Discovery Scope
- Q: "Which capabilities should I look up in the marketplaces (github/awesome-copilot, github/copilot-plugins, anthropics/skills, openai/skills, OpenCode catalogs, Gemini extensions)? (comma-separated, e.g., 'playwright, azure, postgres')"
- Freeform. Allow `skip`.

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

### 11d. Audit evidence
- Q: "What audit evidence should agents preserve?"
- Choices: `["Diff summary only", "Test/build evidence", "Security findings", "Decision records / ADRs", "Compliance evidence", "Unsure"]`

### 11e. Architecture style
- Q: "What architecture style should the agents preserve or move toward?"
- Choices: `["Layered", "Clean/Hexagonal", "Event-driven", "Microservices", "Modular monolith", "Serverless", "CLI/library", "Unsure"]`

### 11f. Critical qualities
- Q: "Which quality attributes matter most?"
- Choices: `["Security", "Reliability", "Maintainability", "Performance", "Cost", "Accessibility", "Compliance"]`

### 11g. Design anti-patterns
- Q: "Any architecture or design anti-patterns to avoid?"
- Freeform. Allow blank.

### 11h. Output profile / context budget
- Q: "How much detail should generated agent files include?"
- Choices: `["Balanced (Recommended)", "Compact", "Full"]`
- Record as `output_profile`. If the user is unsure, choose `Balanced`.

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
