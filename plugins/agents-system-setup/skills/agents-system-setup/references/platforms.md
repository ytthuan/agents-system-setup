# Multi-Platform Emission Reference

This skill targets three agent runtimes. The user picks one or more in **Phase 0** of the interview; the generator loops over the selection.

## Supported Platforms

| Platform | Docs |
|---|---|
| **Copilot CLI** | https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents |
| **Claude Code** | https://docs.anthropic.com/en/docs/claude-code/sub-agents |
| **OpenCode** | https://opencode.ai/docs/agents/ · https://opencode.ai/docs/mcp-servers/ |
| **OpenAI Codex CLI** | https://github.com/openai/codex · https://agents.md |

## Path / Format Matrix

| Artifact | Copilot CLI | Claude Code | OpenCode | OpenAI Codex CLI |
|---|---|---|---|---|
| Agents | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | `.opencode/agents/<name>.md` | orchestrator + project rules in `AGENTS.md`; **specialized subagents in `.codex/agents/<name>.toml`** (project) or `~/.codex/agents/` (user) |
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` | not supported natively — describe in `AGENTS.md` |
| MCP servers | `.mcp.json` (root) | `.mcp.json` (root, shared with Copilot) | `opencode.json` › `"mcp": { ... }` | `.mcp.json` (root, shared) |
| Hooks | `.github/hooks/*.json` | `.claude/settings.json` › `"hooks"` | `.opencode/hooks/` | not supported |
| Project memory | `AGENTS.md` (root) | `CLAUDE.md` (symlink → `AGENTS.md` on macOS/Linux; copy on Windows) | `AGENTS.md` (native) | `AGENTS.md` (native — primary consumer) |
| Personal memory | `~/.copilot/AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.config/opencode/AGENTS.md` | `~/.codex/AGENTS.md` |

## Agent Frontmatter — per platform

### Copilot CLI (`.agent.md`)
```yaml
---
name: planner
description: 'Use when ...'
model: claude-sonnet-4.6        # optional
tools: [view, grep, glob, bash] # optional whitelist
mcp-servers:                    # optional, hyphenated key
  github: { command: npx, args: [...], env: {...} }
---
```

### Claude Code (`.md` under `.claude/agents/`)
Only `name` + `description` required. Defaults: `model: inherit`, all tools inherited from parent. Source: https://docs.claude.com/en/docs/claude-code/sub-agents
```yaml
---
name: planner                    # REQUIRED — lowercase + hyphens, unique, matches filename
description: Use when ...        # REQUIRED — drives delegation
tools: Read, Grep, Glob, Bash    # optional comma-string allowlist; omit = inherit all
disallowedTools: Write, Edit     # optional denylist (applied before `tools`)
model: sonnet                    # optional: sonnet | opus | haiku | <full-id> | inherit (default)
permissionMode: default          # optional: default | acceptEdits | auto | dontAsk | bypassPermissions | plan
skills: [code-review]            # optional: full skill body injected (subagents do NOT inherit parent skills)
mcpServers: { slack: {} }        # optional: name ref or inline config
isolation: worktree              # optional: isolated git worktree copy
color: blue                      # optional UI color
# Also: maxTurns, hooks, memory (user|project|local), background, effort, initialPrompt
---
```
> Tool names are Claude's canonical names (`Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `Task`, `WebFetch`). Do **not** copy Copilot tool names verbatim. Scope precedence: managed settings > `--agents` CLI > project (`.claude/agents/`) > user (`~/.claude/agents/`) > plugin.

### OpenCode (`.md` under `.opencode/agents/` or `~/.config/opencode/agents/`)
Only `description` required. Filename = agent name. `tools:` is deprecated — prefer `permission`. Source: https://opencode.ai/docs/agents/
```yaml
---
description: Use when ...                                  # REQUIRED
mode: subagent                                             # primary | subagent | all (default: all)
model: anthropic/claude-sonnet-4-20250514                  # provider/model-id
temperature: 0.1                                           # optional
prompt: "{file:./prompts/review.txt}"                      # optional external system prompt
steps: 5                                                   # optional max agentic iterations
hidden: false                                              # hide from @ autocomplete
permission:                                                # preferred over deprecated `tools:`
  edit: deny                                               # allow | ask | deny
  webfetch: deny
  bash:
    "*": ask                                               # wildcard FIRST, specific after (last match wins)
    "git status *": allow
  task:                                                    # gate Task-tool subagent invocation
    "*": deny
    "code-reviewer": allow
---
```
> MCP servers live in `opencode.json` › `mcp`, NOT in agent frontmatter. Built-in primaries: `build`, `plan`. Built-in subagents: `general`, `explore`. Extra top-level keys (e.g. `reasoningEffort`) pass through as provider model options.

### OpenAI Codex CLI — split layout

**Project rules + orchestrator** live in `AGENTS.md` at the repo root (Codex's primary input). `## <Display Name>` headings inside `AGENTS.md` are reserved for **the orchestrator and shared project-wide concerns** (Directory Architecture, Capability Matrix, Waves) — *not* specialized workers.

**Specialized subagents** are standalone TOML files under `.codex/agents/<name>.toml` (project-scoped) or `~/.codex/agents/<name>.toml` (user-scoped). Codex loads each file as a configuration layer for the spawned session, so a custom agent file may override any setting a normal session config sets. Switch threads with `/agent` in the CLI.

**Required fields** (per [openai docs](https://developers.openai.com/codex/subagents)):

| Field                    | Type     | Purpose                                                         |
| ------------------------ | -------- | --------------------------------------------------------------- |
| `name`                   | string   | Source of truth for the agent identity (filename is convention only). |
| `description`            | string   | Human-facing guidance for when Codex should use this agent.     |
| `developer_instructions` | string   | Core instructions defining behavior (use TOML triple-quoted string). |

**Optional fields** (inherit from parent session if omitted): `nickname_candidates: string[]`, `model`, `model_reasoning_effort` (`low`|`medium`|`high`), `sandbox_mode` (e.g. `read-only`, `workspace-write`), `[mcp_servers.<id>]` table, `[[skills.config]]` array. Built-in agent names — `default`, `worker`, `explorer` — can be overridden by a custom file using the same `name`.

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings, include reproduction steps when possible.
"""
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

**Global subagent settings** live under `[agents]` in `.codex/config.toml`:

```toml
[agents]
max_threads = 6   # default 6
max_depth = 1     # default 1; raise only if you truly need recursive delegation
```

Codex reads `.mcp.json` at repo root (shared with Copilot/Claude). Per-agent MCP servers may also be declared inline via `[mcp_servers.<id>]` in the agent's TOML.

## MCP Configuration — per platform

### Copilot CLI / Claude Code (`.mcp.json` at repo root)
```jsonc
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
    }
  }
}
```

### OpenCode (`opencode.json` at repo root)
```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_PERSONAL_ACCESS_TOKEN}" },
      "enabled": true
    }
  }
}
```
> OpenCode merges `opencode.json` non-destructively when other config keys exist — preserve them.

## Project-Memory Linking

If both Copilot/OpenCode (use `AGENTS.md`) and Claude Code (uses `CLAUDE.md`) are selected:

- **macOS/Linux**: `ln -s AGENTS.md CLAUDE.md`
- **Windows**: copy `AGENTS.md` → `CLAUDE.md` and prepend `<!-- generated from AGENTS.md — re-copy on every update -->`. Re-copy on each `update` run.

Detect platform with `uname -s` (Darwin/Linux ⇒ symlink; otherwise copy).

## Generation Loop (pseudocode)

```
for platform in selected_platforms:
    paths   = PATH_MATRIX[platform]
    fmt     = FRONTMATTER[platform]
    for agent in agents:
        write(paths.agents / f"{agent.name}{paths.agent_suffix}",
              render(agent, fmt))
    for skill in skills:
        write(paths.skills / skill.name / "SKILL.md", render(skill))
    if approved_mcp_servers:
        merge(paths.mcp_config, approved_mcp_servers, format=fmt.mcp)
link_project_memory(selected_platforms)
```

## Anti-patterns

- Writing Copilot frontmatter to a `.claude/agents/*.md` file (Claude will silently ignore unknown keys).
- Using `mcp-servers:` (hyphen) in OpenCode — OpenCode uses top-level `mcp` in `opencode.json`, not per-agent.
- Symlinking `CLAUDE.md` on Windows.
- Overwriting `opencode.json` instead of merging the `mcp` key.
