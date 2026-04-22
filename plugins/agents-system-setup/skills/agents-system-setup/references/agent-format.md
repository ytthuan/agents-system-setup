# Custom Agent Format — per platform

This skill targets three runtimes. **Use the right schema for each** — agents written in Copilot frontmatter will be silently ignored by Claude Code, and vice versa.

For path matrix and full examples, see [platforms.md](./platforms.md).

## Copilot CLI (`.github/agents/<name>.agent.md`)

Source: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents#agent-profile-format
How-to: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli

```markdown
---
name: <kebab-case-name>           # MUST match filename basename
description: 'Use when ... <trigger keywords>.'
model: claude-sonnet-4.6          # OPTIONAL
tools:                            # OPTIONAL whitelist; omit = inherit all
  - bash
  - view
  - edit
  - create
  - grep
  - glob
mcp-servers:                      # OPTIONAL — hyphenated key
  github:
    command: npx
    args: ['-y', '@modelcontextprotocol/server-github']
    env: { GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_PERSONAL_ACCESS_TOKEN} }
---

# <Display Name>
(prompt body)
```

## Claude Code (`.claude/agents/<name>.md`)

Source: https://docs.anthropic.com/en/docs/claude-code/sub-agents

```markdown
---
name: <kebab-case-name>
description: Use when ... <triggers>.
tools: Read, Grep, Glob, Bash     # OPTIONAL — comma-separated string; omit for all
model: sonnet                     # OPTIONAL — opus | sonnet | haiku | inherit
---

You are a <role>...
(prompt body)
```

> Tool names are Claude's canonical names: `Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `Task`, `WebFetch`. Do **not** use Copilot's tool names here.

## OpenCode (`.opencode/agents/<name>.md`)

Source: https://opencode.ai/docs/agents/

```markdown
---
description: Use when ...
mode: subagent                    # primary | subagent | all
model: anthropic/claude-sonnet-4-5    # OPTIONAL — provider/model
temperature: 0.1                  # OPTIONAL
tools:                            # OPTIONAL — bool-keyed map
  write: false
  edit: false
  bash: true
permission:                       # OPTIONAL — fine-grained gates
  edit: ask                       # allow | ask | deny
  bash:
    "git push": deny
mcp:                              # NOTE: project MCP lives in opencode.json, not here
  []
---

You are a <role>...
```

> OpenCode does not embed MCP servers in agent frontmatter — put them in `opencode.json` › `mcp`. Per-agent gating uses `permission:`.

## OpenAI Codex CLI — split layout: `AGENTS.md` + `.codex/agents/*.toml`

Source: https://developers.openai.com/codex/subagents · general AGENTS.md spec: https://agents.md

Codex uses **two complementary surfaces**:

1. **`AGENTS.md`** at the repo root — project memory + orchestrator instructions + Directory Architecture / Capability Matrix / Waves. The orchestrator MAY appear here as `## Orchestrator`.
2. **`.codex/agents/<name>.toml`** (project) or **`~/.codex/agents/<name>.toml`** (user) — one TOML file per specialized subagent. Codex loads each as a session config layer; switch with `/agent`.

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "gpt-5.4"                       # optional; inherits from session if omitted
model_reasoning_effort = "high"         # optional: low|medium|high
sandbox_mode = "read-only"              # optional: read-only|workspace-write
nickname_candidates = ["Atlas", "Delta"]  # optional, presentation only
developer_instructions = """
You are a senior reviewer. Lead with concrete findings.
Prioritize correctness, security, behavior regressions, and missing tests.
"""

[mcp_servers.openaiDeveloperDocs]       # optional, per-agent MCP allowlist
url = "https://developers.openai.com/mcp"

[[skills.config]]                        # optional, per-agent skill toggle
path = "/abs/path/to/SKILL.md"
enabled = false
```

Codex CLI rules:
- **Required fields**: `name`, `description`, `developer_instructions`. Missing any → silent skip.
- **`name` is the source of truth** (filename is convention only). Custom files may override built-ins (`default`, `worker`, `explorer`) by reusing the name.
- **Global config** in `.codex/config.toml`: `[agents] max_threads = 6` and `max_depth = 1` defaults.
- MCP servers can be shared via `.mcp.json` at repo root *or* declared per-agent inside the TOML.
- Skills: per-agent enable/disable via `[[skills.config]]` array entries.

## Discovery Surface (all platforms)

The router/orchestrator picks a subagent based on the **`description`** field (or `description` in `.codex/agents/<name>.toml` for Codex).

- Always start with `"Use when ..."`
- Include concrete trigger keywords from the user's domain
- Quote any description containing colons

## Common Pitfalls

- `name` mismatch with filename → silent ignore (Copilot, Claude).
- Unquoted colon in `description` → YAML parse failure → silent ignore.
- Missing `description` → never auto-invoked.
- Using Copilot's `tools:` *list* in a Claude file (Claude expects a comma-separated *string*).
- Using Claude's `model: sonnet` in an OpenCode file (OpenCode expects `provider/model`).
- Embedding `mcp-servers:` in an OpenCode agent (use `opencode.json` instead).
- Overlapping responsibilities between two subagents → orchestrator picks wrong one. Make boundaries explicit in `## Out of scope` and in the **Directory Architecture** in `AGENTS.md`.

## Tool Restriction Patterns (use the platform's syntax)

| Pattern | Copilot CLI | Claude Code | OpenCode | Codex CLI |
|---|---|---|---|---|
| Read-only reviewer | `tools: [view, grep, glob, bash]` | `tools: Read, Grep, Glob, Bash` | `tools: { write: false, edit: false, bash: true }` | `sandbox_mode = "read-only"` in `.codex/agents/<name>.toml` |
| Implementer (full) | omit `tools:` | omit `tools:` | omit `tools:` (or all true) | `sandbox_mode = "workspace-write"` (or omit to inherit) |
| Docs writer | `tools: [view, edit, create]` | `tools: Read, Edit, Write` | `tools: { bash: false }` | `sandbox_mode = "workspace-write"`; describe scope in `developer_instructions` |

## MCP Per-Agent Reference

- **Copilot CLI** — list servers under `mcp-servers:` in agent frontmatter, or define centrally in `.mcp.json`.
- **Claude Code** — central `.mcp.json` (shared with Copilot when both target the repo).
- **OpenCode** — central `opencode.json` `mcp` key only; agents reference by name via the runtime's discovery.

**Any change to MCP requires the Phase 3.5 approval gate.**
