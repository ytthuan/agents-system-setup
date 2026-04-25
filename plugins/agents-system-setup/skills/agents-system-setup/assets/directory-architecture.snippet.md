<!-- Drop-in snippet: paste into any agent file under "## Hard Rules" -->

## Directory Boundaries — non-negotiable

Before any edit, **read `AGENTS.md` › Directory Architecture**.
Before risky edits, also read `AGENTS.md` › **Security & Audit Matrix**, **Threat Model**, **Architecture & Design Pattern Decisions**, and **Quality Gates**.

- I write only to paths listed under my **Owned paths**.
- I may read paths marked `read-only` for context.
- For `shared` paths, I coordinate with the orchestrator before writing.
- For paths owned by another agent, I return control to `@orchestrator` and request delegation.
- For secrets, MCP/tool config, auth, dependency manifests, CI/release config, generated scripts, or deployment settings, I return explicit audit evidence in my final output.

Violations of this rule are bugs. Stop and report instead.
