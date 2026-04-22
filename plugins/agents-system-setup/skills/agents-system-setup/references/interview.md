# Interview Script

Use `ask_user` for **every** question. One question per call. Multiple-choice when possible (the runtime adds a freeform option automatically — never include "Other" in choices).

## 0. Platform Selection (FIRST question after detection)
- Q: "Which agent runtime(s) should I configure?"
- Choices: `["Copilot CLI only (Recommended for GitHub-centric teams)", "Claude Code only", "OpenCode only", "Copilot CLI + Claude Code", "All three (Copilot CLI + Claude Code + OpenCode)"]`

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
- Q: "Where should the agents/skills live?"
- Choices: `["Project (team-shared) (Recommended)", "Personal (only for me)"]`

## 9. Subagent Topology
- Show the suggestion derived from project type via [topology.md](./topology.md).
- Q: "Suggested subagents: <list>. Accept, add, or remove?"
- Freeform with the suggested list pre-printed.

## 9b. Per-Agent Model Override (optional, ask only if user wants to set models)
- Q: "Want to set a custom model for any agent? (Leave blank for platform default)"
- Choices: `["No, use platform default for all (Recommended)", "Yes, I'll specify per agent"]`
- If yes: loop per agent name, freeform model id (e.g., `claude-sonnet-4.6`, `sonnet`, `anthropic/claude-sonnet-4-5`). Skip leaves model blank.

## 10. Plugin / Skill / MCP Discovery Scope
- Q: "Which capabilities should I look up in the marketplaces (github/copilot-plugins, github/awesome-copilot, anthropics/skills, claudeforge/marketplace)? (comma-separated, e.g., 'playwright, azure, postgres')"
- Freeform. Allow `skip`.

## 10b. MCP Approval Mode (only if any MCP server is among selections later)
- Q: "How should I handle MCP server config writes when we get to the approval gate?"
- Choices: `["Approve all at once after I show the config (Recommended)", "Approve selectively, per server", "Skip MCP entirely — recommend in plan only, write nothing"]`

## 11. Git
- Only if no `.git/` present.
- Q: "No git repo detected. Run `git init` + `.gitignore` + initial commit?"
- Choices: `["Yes (Recommended)", "No, leave git untouched"]`

## 12. Plan Approval (after Phase 2)
- Q: "Here is the plan: <render>. Proceed?"
- Choices: `["Yes, proceed", "Edit plan first"]`

## 13. Per-Capability Recommendation Choice (Phase 3, looped)
- One call per capability the user named in Q10.
- Q: "For capability **<x>**, which would you like?"
- Choices built dynamically: `["<candidate 1 — name + tier>", "<candidate 2>", "<candidate 3>", "Show more (Tier-3 fallback)", "None — skip this capability"]`
