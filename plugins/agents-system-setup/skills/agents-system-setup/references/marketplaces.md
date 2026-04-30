# Well-Known Marketplaces & Catalogs (lookup order)

> Last verified: 2026-04-29. Star counts are approximate; check the upstream link for current state.
>
> Doc anchors:
> - Copilot CLI plugins: <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins>
> - Claude Code plugins: <https://docs.claude.com/en/docs/claude-code/plugins>
> - Codex CLI plugins (build): <https://developers.openai.com/codex/plugins/build>
> - Codex CLI plugins (use): <https://developers.openai.com/codex/plugins>
> - Codex CLI + App subagents: <https://developers.openai.com/codex/subagents>
> - OpenCode plugins/agents: <https://opencode.ai/docs/agents/>
> - Gemini CLI subagents: <https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md>
> - Gemini CLI extensions: <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md>

A "marketplace" is a registry where plugins (which can bundle agents, skills, hooks, MCP server configs, LSP server configs) are published. Always search Tier 1 first, then Tier 2; only fall back to free-text `github-search_repositories` if all of them miss.

## Tier 1 — Vendor-official (always check first)

| Marketplace / Catalog | URL | Vendor | What's there |
|---|---|---|---|
| `github/awesome-copilot` | <https://github.com/github/awesome-copilot> | GitHub | Community-contributed instructions, agents, skills, configs (~30k★). Official Copilot curation. |
| `github/copilot-plugins` | <https://github.com/github/copilot-plugins> | GitHub | Reference Copilot CLI plugin samples (agents, skills, hooks, MCP) |
| `anthropics/skills` | <https://github.com/anthropics/skills> | Anthropic | Reference Agent Skills (open standard) |
| `anthropics/claude-code` | <https://github.com/anthropics/claude-code> | Anthropic | Claude Code core repo + sub-agent format source-of-truth |
| `openai/skills` | <https://github.com/openai/skills> | OpenAI | **Skills Catalog for Codex** (~17k★). Authoritative skill registry. |
| `openai/plugins` | <https://github.com/openai/plugins> | OpenAI | OpenAI plugins (~900★) |
| `openai/codex` | <https://github.com/openai/codex> | OpenAI | OpenAI Codex core (~77k★); shared artifacts use `AGENTS.md` + `.codex/agents/*.toml`; plugin manifests may bundle `skills`, `mcpServers`, `apps`, interface assets, `.app.json`, and `.mcp.json` |
| `openai/codex-plugin-cc` | <https://github.com/openai/codex-plugin-cc> | OpenAI | Use Codex from Claude Code (cross-runtime bridge, ~15k★) |
| `google-gemini/gemini-cli` | <https://github.com/google-gemini/gemini-cli> | Google | Gemini CLI docs, local subagent schema, extension format, and source-backed loader behavior. |
| Gemini CLI extension gallery | <https://geminicli.com/extensions/browse/> | Google/Gemini ecosystem | Discoverable Gemini extensions that may bundle MCP servers, commands, hooks, skills, and subagents. Verify source repo and manifest before recommending. |
| `modelcontextprotocol/servers` | <https://github.com/modelcontextprotocol/servers> | MCP project | Reference MCP servers (filesystem, github, git, fetch, …) |
| GitHub Code Security docs | <https://docs.github.com/en/code-security> | GitHub | Source-of-truth for secret scanning, code scanning, dependency review, Dependabot, push protection |
| OWASP GenAI Security | <https://owasp.org/www-project-top-10-for-large-language-model-applications/> | OWASP | Agentic AI / LLM threat categories and review checklist |
| MCP Security Best Practices | <https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices> | MCP project | MCP authorization, confused deputy, token, and transport risk guidance |

## Tier 2 — High-signal community catalogs (cross-checked, current)

### General / cross-runtime

| Source | URL | Coverage |
|---|---|---|
| `wshobson/agents` | <https://github.com/wshobson/agents> | Claude Code multi-agent orchestration (~34k★) — large agent + skill collection |
| `obra/superpowers` | <https://github.com/obra/superpowers> | Agentic skills framework + methodology |
| `EveryInc/compound-engineering-plugin` | <https://github.com/EveryInc/compound-engineering-plugin> | Cross-runtime plugin (Claude Code, Codex, Cursor, …) |
| `numman-ali/n-skills` | <https://github.com/numman-ali/n-skills> | Curated plugin marketplace, multi-runtime |
| `gmh5225/awesome-skills` | <https://github.com/gmh5225/awesome-skills> | Cross-tool skill index (Claude / Codex / Gemini / Copilot) |
| `safishamsi/graphify` | <https://github.com/safishamsi/graphify> | Multi-runtime skill (Claude / Codex / OpenCode / Copilot / Cursor) — knowledge-graph example |

### Claude Code

| Source | URL | Notes |
|---|---|---|
| `hesreallyhim/awesome-claude-code` | <https://github.com/hesreallyhim/awesome-claude-code> | Skills, hooks, slash-commands, agent orchestrators (~40k★) |
| `rohitg00/awesome-claude-code-toolkit` | <https://github.com/rohitg00/awesome-claude-code-toolkit> | 135 agents, 35 skills, 42 commands, 176+ plugins, hooks/rules/MCP |
| `helloianneo/awesome-claude-code-skills` | <https://github.com/helloianneo/awesome-claude-code-skills> | 50+ curated skills/agents/plugins (CN/EN, scenario-grouped) |
| `vijaythecoder/awesome-claude-agents` | <https://github.com/vijaythecoder/awesome-claude-agents> | Orchestrated sub-agent dev-team templates |
| `ComposioHQ/awesome-claude-plugins` | <https://github.com/ComposioHQ/awesome-claude-plugins> | Commands, agents, hooks, MCP |
| `alexei-led/cc-thingz` | <https://github.com/alexei-led/cc-thingz> | Battle-tested marketplace: 27 skills, 34 agents, 9 hooks (Claude/Codex/Gemini) |

### Copilot CLI / VS Code

| Source | URL | Notes |
|---|---|---|
| `Code-and-Sorts/awesome-copilot-agents` | <https://github.com/Code-and-Sorts/awesome-copilot-agents> | Copilot agents/skills/MCP curated index |
| `dfinke/awesome-copilot-chatmodes` | <https://github.com/dfinke/awesome-copilot-chatmodes> | VS Code Copilot chat-mode personas |

### OpenCode

| Source | URL | Notes |
|---|---|---|
| `awesome-opencode/awesome-opencode` | <https://github.com/awesome-opencode/awesome-opencode> | Curated OpenCode plugins, themes, agents, projects (~5.5k★) |

### Gemini CLI

| Source | URL | Notes |
|---|---|---|
| `google-gemini/gemini-cli` subagents docs | <https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md> | Official local subagent format: `.gemini/agents/*.md`, user `~/.gemini/agents/*.md`, extension `agents/*.md`; `@<agent>` invocation; non-recursive subagents. |
| `google-gemini/gemini-cli` loader schema | <https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/agents/agentLoader.ts> | Source-backed validation: required `name`/`description`, optional `display_name`, `tools`, `mcp_servers`, `model`, `temperature`, `max_turns`, `timeout_mins`; remote A2A fields are import/advanced only. |
| `google-gemini/gemini-cli` extension docs | <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md> | Extension-bundled prompts, MCP servers, commands, hooks, skills, and subagents. |
| Gemini CLI extension gallery | <https://geminicli.com/extensions/browse/> | Browse extensions, then inspect the source repo/manifest before recommending. |

### OpenAI Codex / `AGENTS.md` ecosystem

| Source | URL | Notes |
|---|---|---|
| `Ischca/awesome-agents-md` | <https://github.com/Ischca/awesome-agents-md> | Real-world `AGENTS.md` files + templates |

### Domain-specific skill packs (good prior art)

| Source | URL | Domain |
|---|---|---|
| `dotnet/skills` | <https://github.com/dotnet/skills> | .NET / C# (Microsoft-owned) |
| `kepano/obsidian-skills` | <https://github.com/kepano/obsidian-skills> | Obsidian (Markdown / Bases / Canvas) |
| `microsoft/GitHub-Copilot-for-Azure` | <https://github.com/microsoft/GitHub-Copilot-for-Azure> | Azure (official) |

### Security, audit, architecture, and policy references

These are not all "plugins", but they are approved source material for the governance baseline and for recommending tools or checks.

| Source | URL | Use |
|---|---|---|
| NIST SSDF SP 800-218 | <https://csrc.nist.gov/Projects/ssdf> | Secure development practice map (PO, PS, PW, RV) |
| SLSA v1.1 | <https://slsa.dev/spec/v1.1/> | Build provenance and supply-chain integrity requirements |
| Open Policy Agent | <https://www.openpolicyagent.org/docs/latest/> | Policy-as-code prior art for CI/CD, Kubernetes, API gateways, and config checks |
| Azure Well-Architected Framework | <https://learn.microsoft.com/en-us/azure/well-architected/> | Cloud architecture quality pillars and review structure |
| C4 Model | <https://c4model.com/> | Context/container/component architecture views |
| TOGAF Standard | <https://www.opengroup.org/togaf> | Enterprise architecture framing for large organizations only |

## Tier 3 — Topic search (fallback only)

When tiers 1–2 yield nothing for a capability:

```
github-search_repositories topic:mcp <capability>
github-search_repositories topic:copilot-plugin <capability>
github-search_repositories topic:claude-code-plugin <capability>
github-search_repositories topic:claude-code-skills <capability>
github-search_repositories topic:codex-skills <capability>
github-search_repositories topic:opencode-skills <capability>
github-search_repositories topic:gemini-cli-extension <capability>
github-search_repositories topic:gemini-cli-agent <capability>
github-search_repositories topic:agent-skills <capability>
github-search_repositories topic:codeql <capability>
github-search_repositories topic:openssf <capability>
github-search_repositories topic:slsa <capability>
github-search_repositories topic:opa <capability>
github-search_repositories "<capability> mcp server" in:name,description
```

## Vendor-attribution rule

When recommending an item, always tag it with the source tier and vendor so provenance is auditable:

```
[Tier 1 · Anthropic] anthropics/skills/<skill-name> — ...
[Tier 1 · GitHub]    github/awesome-copilot/agents/<name> — ...
[Tier 1 · OpenAI]    openai/skills/<skill-name> — ...
[Tier 1 · OWASP]     OWASP GenAI Security / LLM Top 10 — ...
[Tier 1 · GitHub]    GitHub Code Security — ...
[Tier 1 · MCP]       MCP Security Best Practices — ...
[Tier 2 · Community] hesreallyhim/awesome-claude-code → entry "<name>" — ...
```

This prevents the user from accepting an unmaintained fork and makes the recommendation list reviewable.

## Install patterns — per runtime

### Copilot CLI

```
copilot
> /plugin install <owner>/<repo>
> /plugin install <owner>/<repo>/<plugin-subpath>
```

### Claude Code

```
claude
> /plugin install <owner>/<repo>
# Skills are namespaced as /<plugin>:<skill>
```

### OpenAI Codex CLI install

```
codex plugin marketplace add <owner>/<repo>
codex plugin marketplace add <owner>/<repo> --ref main
codex plugin marketplace add <owner>/<repo> --sparse .agents/plugins
codex
> /plugins        # browse and install
> @<plugin-name>  # invoke a plugin or its bundled skill
```

Codex marketplace sources accept GitHub shorthand, HTTPS/SSH Git URLs, or a local path. Refresh with `codex plugin marketplace upgrade [name]`; remove with `codex plugin marketplace remove <name>`. These are CLI plugin commands; do not present them as Codex App plugin installation.

### OpenCode

OpenCode "plugins" are JS/TS hooks (different shape from the other runtimes). Skill-style content is installed by clone-and-copy under `~/.config/opencode/skills/` (user) or `.opencode/skills/` (project). Agent Markdown belongs under `~/.config/opencode/agents/` or `.opencode/agents/`. MCP servers go in `opencode.json` › `mcp`.

### Gemini CLI

Artifact-first Gemini usage:

```text
.gemini/agents/<agent-name>.md
GEMINI.md
gemini
> /agents
> @<agent-name> <task>
```

Gemini extension recommendations must identify what the extension actually ships: `gemini-extension.json`, MCP servers (`mcpServers` in extension manifests), commands, hooks, skills, context files, and/or `agents/*.md`. Do not claim a generic Gemini plugin install path for this package. Project-local generated subagents go under `.gemini/agents/*.md`; inline MCP belongs under loader-valid `mcp_servers:` and stays approval-gated.

## What a plugin can ship (cross-runtime cheat sheet)

| Component                | Copilot | Claude Code | Codex | OpenCode | Gemini CLI |
|--------------------------|:---:|:---:|:---:|:---:|:---:|
| Agents (per-file)        | `.github/agents/*.agent.md` | `agents/*.md` | `.codex/agents/*.toml` | `.opencode/agents/*.md` | `.gemini/agents/*.md` or extension `agents/*.md` |
| Skills                   | `skills/<name>/SKILL.md` | `skills/<name>/SKILL.md` | `skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` | extension `skills/<name>/SKILL.md` |
| Hooks                    | `hooks.json` | `hooks/hooks.json` | (planned) | JS/TS hooks | extension hooks |
| MCP servers              | `.mcp.json` (or `.github/mcp.json`) | `.mcp.json` (also inline in agent `mcpServers`) | `.mcp.json` (also inline `[mcp_servers.*]` per agent) | `opencode.json` › `mcp` | agent `mcp_servers:` or extension `mcpServers` |
| LSP servers              | `lsp.json` | `.lsp.json` | n/a | n/a | n/a |
| Slash commands           | n/a | `commands/` (legacy) → `skills/` (new) | `skills/` | n/a | extension `commands/` |

Always inspect a plugin's README before recommending — surface what it actually brings to the user.
