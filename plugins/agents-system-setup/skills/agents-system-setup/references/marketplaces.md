# Well-Known Marketplaces (lookup order)

Source: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins

A "marketplace" is a registry where plugins (which can bundle agents, skills, hooks, MCP server configs, LSP server configs) are published. Always search these in order; only fall back to free-text `github-search_repositories` if all of them miss.

## Tier 1 — Vendor-official (search first)

| Marketplace | URL | Vendor | What's there |
|---|---|---|---|
| `github/copilot-plugins` | https://github.com/github/copilot-plugins | GitHub | Official Copilot CLI plugins (agents, skills, hooks, MCP) |
| `github/awesome-copilot` | https://github.com/github/awesome-copilot | GitHub | Official curated community plugins, skills, prompts (30k+ ★) |
| `anthropics/skills` | https://github.com/anthropics/skills | Anthropic | Reference Agent Skills (open standard) |
| `anthropics/claude-code` | https://github.com/anthropics/claude-code | Anthropic | Claude Code core + plugins (sub-agent format source) |
| `openai/codex` | https://github.com/openai/codex | OpenAI | Codex CLI (consumes `AGENTS.md`); MCP via `.mcp.json` |
| `modelcontextprotocol/servers` | https://github.com/modelcontextprotocol/servers | MCP project | Reference MCP servers (filesystem, github, git, fetch, …) |

## Tier 2 — High-signal community awesome-lists

| Source | URL | Coverage |
|---|---|---|
| `Code-and-Sorts/awesome-copilot-agents` | https://github.com/Code-and-Sorts/awesome-copilot-agents | Copilot agents/skills/MCP curated index |
| `hesreallyhim/awesome-claude-code` | https://github.com/hesreallyhim/awesome-claude-code | Claude Code skills, hooks, slash-commands, agent orchestrators (40k+ ★) |
| `vijaythecoder/awesome-claude-agents` | https://github.com/vijaythecoder/awesome-claude-agents | Orchestrated sub-agent dev team templates for Claude Code |
| `ComposioHQ/awesome-claude-plugins` | https://github.com/ComposioHQ/awesome-claude-plugins | Claude Code plugins (commands, agents, hooks, MCP) |
| `Ischca/awesome-agents-md` | https://github.com/Ischca/awesome-agents-md | Real-world `AGENTS.md` files & templates (OpenAI Codex / agents.md spec) |
| `JackyST0/awesome-agent-skills` | https://github.com/JackyST0/awesome-agent-skills | Cross-tool skill list (Cursor, Claude, Copilot) |
| `dfinke/awesome-copilot-chatmodes` | https://github.com/dfinke/awesome-copilot-chatmodes | VS Code Copilot chat-mode personas |

## Tier 3 — Topic search (fallback only)

When tiers 1–2 yield nothing for a capability:

```
github-search_repositories topic:mcp <capability>
github-search_repositories topic:copilot-plugin <capability>
github-search_repositories topic:claude-code-plugin <capability>
github-search_repositories topic:agent-skills <capability>
github-search_repositories "<capability> mcp server" in:name,description
```

## Vendor-attribution rule

When recommending an item, always tag it with the source tier and vendor:

```
[Tier 1 · Anthropic] anthropics/skills/markdown-validator — ...
[Tier 1 · GitHub]    github/awesome-copilot/agents/security-reviewer — ...
[Tier 1 · OpenAI]    openai/codex (consumes AGENTS.md natively) — ...
[Tier 2 · Community] hesreallyhim/awesome-claude-code → entry "subagent-orchestrator" — ...
```

This makes provenance auditable and prevents the user from accepting an unmaintained fork.

## Install Pattern

Once a plugin is chosen, it is installed via the CLI:

```
/plugin install <owner>/<repo>
# or
/plugin install <owner>/<repo>/<plugin-subpath>
```

A plugin can ship: `agents/*.agent.md`, `skills/<name>/SKILL.md`, `hooks.json`, `.mcp.json` (or `.github/mcp.json`), `lsp.json`. Inspect the plugin README before recommending — surface what it brings to the user.

## Doc Anchors

- Plugins concept: https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins
- Finding/installing plugins: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing
- Agent skills: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- Custom agents (CLI how-to): https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
- Custom agents (profile format): https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents#agent-profile-format
