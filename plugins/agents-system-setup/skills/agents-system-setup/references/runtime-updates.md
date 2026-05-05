# Runtime Update Audit

> Last verified: 2026-05-05. This file records upstream runtime drift that affects generation, replication, and validation. It is source material for the supported-runtime docs, not a generated user artifact.

## Support policy

| Status | Meaning | Runtime handling |
|---|---|---|
| Supported | The plugin emits artifacts and validates schemas for the runtime. | Keep in `SKILL.md`, `platforms.md`, `agent-format.md`, replication IR, marketplace/output docs, validators, and release metadata. |
| Drift noted | Upstream docs or behavior changed, but the current emitter remains valid. | Document the drift, keep existing output stable, and add validator markers so the item is not forgotten. |
| Import / advanced only | Upstream supports a surface that the default generator should not emit. | Parse/audit when encountered, report lossiness, and require explicit user approval before writing. |

Current supported runtimes are **Copilot CLI**, **Claude Code**, **OpenCode**, **OpenAI Codex (CLI + App)**, and **Gemini CLI**.

## Current runtime findings

| Runtime | Sources | Drift category | Required plugin adaptation |
|---|---|---|---|
| Copilot CLI | Concept docs: <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents>; how-to docs: <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli>; config reference: <https://docs.github.com/en/copilot/reference/custom-agents-configuration>; VS Code custom agents (shared `.github/agents/*.agent.md` surface): <https://code.visualstudio.com/docs/copilot/customization/custom-agents>; `/fleet`: <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet> | Filename docs drift + richer tool aliases + standardized tool profile | Keep emitting `.github/agents/<name>.agent.md` while recognizing `.github/agents/<name>.md` as an import signal. Use source-backed tool aliases (`vscode`, `execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`) instead of product-specific internal names. Apply [Copilot CLI Standard Tool Profiles](./platforms.md#copilot-cli-standard-tool-profiles) at emit time: `standard` for orchestrator/edit-capable, `read-only` for reviewers, `runner`/`research` for narrower roles, `inherit` only for explicit opt-out. Document `/fleet` as optional parent-orchestrated fan-out for independent subtasks. |
| Claude Code | Subagents: <https://docs.claude.com/en/docs/claude-code/sub-agents>; agent teams: <https://docs.claude.com/en/docs/claude-code/agent-teams>; plugins: <https://docs.claude.com/en/docs/claude-code/plugins> | Schema split + two parallelism primitives | Distinguish subagent definitions, the tool invocation surface that runs a subagent in one session, and experimental agent teams (separate Claude instances with peer-to-peer messaging). Project/user/session agents may use richer fields such as `mcpServers`, `hooks`, and `permissionMode`; plugin-shipped agents must not rely on unsupported plugin fields. |
| OpenCode | Agents: <https://opencode.ai/docs/agents/>; MCP: <https://opencode.ai/docs/mcp-servers/> | Additive schema + deprecation | Prefer `permission:` over deprecated `tools:`. Document primary vs subagent modes, `@` mention invocation, child-session navigation, Markdown agents, and top-level `opencode.json` `agent` import/update config. Permission keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `todowrite`, `webfetch`, `websearch`, `codesearch`, `lsp`, `skill`, `question`, `doom_loop`. |
| OpenAI Codex (CLI + App) | Subagents: <https://developers.openai.com/codex/subagents>; plugins build: <https://developers.openai.com/codex/plugins/build>; plugins use: <https://developers.openai.com/codex/plugins> | Additive schema | Keep the shared-artifact model: `AGENTS.md`, `.codex/agents/*.toml`, `.codex/config.toml`, and approved `.mcp.json`. Document `agents.max_threads`, `agents.max_depth`, `job_max_runtime_seconds`, `spawn_agents_on_csv`, richer `.codex-plugin/plugin.json` component references (`skills`, `mcpServers`, `apps`, interface assets), `.app.json`, `.mcp.json`, and marketplace metadata guidance. |
| Gemini CLI | Subagents: <https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md>; loader schema: <https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/agents/agentLoader.ts>; extensions: <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md> | Promoted supported runtime + docs/schema naming drift | Emit local project subagents at `.gemini/agents/<name>.md` using YAML frontmatter and Markdown body prompt. Required fields: `name`, `description`; default `kind: local`. Optional fields: `display_name`, `tools`, `mcp_servers`, `model`, `temperature`, `max_turns`, `timeout_mins`. Normalize imported `mcpServers` docs examples to loader-valid `mcp_servers` on emission. Preserve recursion protection: Gemini subagents cannot call other subagents, even with wildcard tools. Treat remote A2A agents as import/advanced only. |

## Drift-handling rules

1. **Do not switch emitters on documentation ambiguity alone.** Copilot keeps `.agent.md` output while importing or auditing `.github/agents/<name>.md` as a documented alternate signal.
2. **Do not mix package schemas with project schemas.** Claude Code plugin-shipped agents are validated separately from project/user/session agents because the plugin surface supports fewer fields.
3. **Prefer current schema over deprecated aliases.** New OpenCode templates use `permission:` and must not introduce deprecated `tools:` blocks.
4. **Keep app/web compatibility separate from CLI-only UX.** Codex shared artifacts must be useful without CLI-only commands; plugin installation and slash commands stay in CLI usage notes.
5. **Emit loader-valid Gemini frontmatter.** Use `mcp_servers:` for Gemini agent-local MCP config even when upstream prose shows `mcpServers`; importers may accept and normalize the docs spelling but must warn on emission.
6. **Never bypass MCP approval gates.** Copilot `mcp-servers:`, Claude `.mcp.json`/`mcpServers`, OpenCode `opencode.json` › `mcp`, Codex `.mcp.json`/TOML `[mcp_servers.*]`, Gemini `mcp_servers:`, and extension/plugin MCP manifests all require the Phase 3.5 gate.
7. **Generated memory is artifact policy, not runtime-native memory.** The Memory & Learning System is rendered into `AGENTS.md`, runtime agent bodies, and approved memory artifacts. Do not claim a runtime has native long-term learning unless source docs confirm it.

## Invocation and packaging audit — 2026-05-05

Source-backed invocation syntax is provider-specific. Do not generalize `/`,
`$`, or `@` across runtimes.

| Runtime | Current invocation / packaging finding | Generator impact |
|---|---|---|
| Copilot CLI | Official command surfaces remain slash-based: `/agent`, `/skills`, `/plugin`, `/mcp`, and `/fleet`. Skills can auto-trigger by description and can be selected through skills slash-command UX; no official `$skill` syntax. Plugin installs must distinguish terminal `copilot plugin install <owner>/<repo>` from in-session `/plugin install PLUGIN@MARKETPLACE`. | Keep emitting `.github/agents/<name>.agent.md`; scan `.github/agents/<name>.md` as an import/upstream-drift signal. Keep plugin install examples split by terminal vs interactive context. |
| Claude Code | Skills auto-load by description and are invoked as `/skill-name`. `$ARGUMENTS`, `$0`, and `$name` are substitution variables, not invocation. Plugin `commands/` remain supported for slash commands; `skills/` are preferred for reusable multi-step workflows. | Do not label Claude plugin `commands/` as legacy-only. Keep plugin skill namespacing and plugin-agent schema split separate from project/user agents. |
| OpenCode | Agents are invoked with `@<agent>`; skills are loaded through the `skill` tool and gated by `permission.skill`; commands live at `.opencode/commands/<name>.md` or config `command` and invoke as `/name`. `$ARGUMENTS` and `$1` are command placeholders. Official plugins are JS/TS or npm/config-based; there is no `opencode plugin install` CLI command. | Keep skills, commands, agents, and plugins as separate surfaces. Document clone/copy or config-based OpenCode plugin installation, not a nonexistent install command. |
| OpenAI Codex (CLI + App) | Skills auto-activate and support explicit `$skill-name` selection plus `/skills` browsing. `/plugins` opens plugin browsing in CLI; the App has a Plugins UI. Typing `@` selects an installed plugin in the composer, but hardcoded plugin-name mentions must not be documented as bundled skill invocation. | Use `$skill-name` or `/skills` for skill examples. Keep CLI-only `/plugins`, `/skills`, `/agent`, and `codex exec` guidance out of shared App artifact requirements. |
| Gemini CLI | Local subagents still use `@<agent>` and `/agents`. Native skills are discovered from `.gemini/skills/<name>/SKILL.md`, compatible `.agents/skills/<name>/SKILL.md`, and user equivalents; users manage skills with `/skills` while the model activates them. Hooks can be native `settings.json` hooks or extension `hooks/hooks.json`. `$VAR` is environment expansion, not skill invocation. | Document native Gemini skills and hooks in addition to extension packaging. Do not generate or document `/<skill>` or `$skill` Gemini invocation. |

## Gemini CLI support notes

Gemini CLI is now a supported fifth runtime for **local project subagents**. Source-backed constraints to preserve:

1. Platform selection and footprint detection include `.gemini/agents/*.md`, `~/.gemini/agents/*.md`, `.gemini/settings.json`, `~/.gemini/settings.json`, and extension `agents/*.md`.
2. Local subagents are Markdown files with YAML frontmatter. The body is the system prompt.
3. Names are slugs (`[a-z0-9-_]+`) and should match the filename basename for predictable routing.
4. `tools:` is an allowlist with wildcard support (`*`, `mcp_*`, `mcp_<server>_*`); if omitted, the subagent inherits parent-session tools.
5. `mcp_servers:` is per-agent MCP config and is isolated to that subagent. It remains approval-gated.
6. `max_turns` and `timeout_mins` map from IR limits. `temperature` maps from model-generation hints.
7. Subagents are invoked automatically by description or explicitly with `@<agent-name>`; the main agent sees each subagent as a tool.
8. Subagents cannot invoke other subagents. Keep cross-agent fan-out in the root/orchestrator session and return cross-boundary work to the orchestrator.
9. Gemini extensions can package prompts, MCP servers, commands, hooks, skills, and subagents. Extension manifests are marketplace/package metadata, not the default project-agent emitter.
10. Remote A2A subagents (`kind: remote`, `agent_card_url`, `agent_card_json`, `auth`) are parsed/imported only when discovered; do not emit them by default.
