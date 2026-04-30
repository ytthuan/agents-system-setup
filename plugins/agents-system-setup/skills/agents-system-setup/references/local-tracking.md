# Local vs Git-Tracked Agent Artifacts

Always ask how generated agent artifacts should be stored before writing project files.

## Modes

| Mode | Use when | Write location | Git behavior |
|---|---|---|---|
| `project-tracked` | Team should share the agent system | Standard project paths (`AGENTS.md`, `GEMINI.md`, `.github/agents/**`, `.claude/**`, `.opencode/**`, `.codex/**`, `.gemini/**`) | Files are normal repo files; do not commit unless user approves git actions. |
| `project-local` | User wants project-specific agents for this checkout only | Standard project paths in the working tree | Add generated paths to `.git/info/exclude`; never modify `.gitignore` just to hide local-only artifacts. |
| `personal-global` | User wants reusable personal agents outside this repo | Runtime user paths (`~/.copilot`, `~/.claude`, `~/.config/opencode`, `~/.codex`) | Nothing written to repo unless explicitly approved. |

## Required question

Ask with `ask_user`:

> "Should the generated agent system be shared through git or kept local to this checkout?"
> Choices: `["Project files, git-tracked (Recommended for teams)", "Project files, local-only / untracked (Recommended for personal setup)", "Personal/global outside this repo"]`

Record the answer as `artifact_tracking`.

## Local-only exclude procedure

For `project-local` in a git repo:

1. Write the requested project-scoped artifacts.
2. Append generated artifact paths to `.git/info/exclude` if missing.
3. Verify `git check-ignore -v <path>` for at least `AGENTS.md`.
4. Report that `.git/info/exclude` is local-only and not committed.

Recommended exclude block:

```gitignore
# agents-system-setup local-only artifacts
AGENTS.md
CLAUDE.md
GEMINI.md
AGENT-TEAMS.md
.agents-system-setup/
.github/agents/
.github/skills/
.claude/agents/
.claude/skills/
.claude/settings.json
.opencode/agents/
.opencode/skills/
.codex/agents/
.codex/config.toml
.gemini/agents/
.gemini/settings.json
.mcp.json
opencode.json
```

Only include paths the skill actually created or modified. If a file already exists and is tracked, do not hide it; ask before changing strategy.

## Anti-patterns

- Writing project-scoped agent files without asking tracking mode.
- Adding local-only artifacts to `.gitignore` in a team repo without approval.
- Excluding all of `.github/` and accidentally hiding workflows or issue templates.
- Treating personal/global installs as project documentation.
