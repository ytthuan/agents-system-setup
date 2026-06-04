# Tool Catalog

Canonical data is `assets/tool-catalog.json`; this reference is the human view of that data. Updates MUST be applied to the JSON first; re-render this reference from the JSON when it diverges. The catalog version in this document is `1.8.0`, matching the first release that treats per-runtime tool naming as an emit-time discipline rather than prose guidance.

## Why this exists

The supported runtimes use incompatible names and configuration shapes for the capabilities that agents can use. Copilot and VS Code share `.github/agents/*.agent.md` but do not expose identical tool sets, Claude Code uses case-sensitive tool names in a comma string, Gemini uses YAML lists and wildcard tool forms, OpenCode has moved from `tools:` to `permission:`, and Codex inherits the parent session toolbelt by default.

This catalog prevents cross-runtime tool name leaks and silent emit-time mistakes. The `audit_kind` field tells generators, validators, and the read-only audit skill which shape to inspect: a name allowlist, a permission policy, or no catalog audit unless an explicit allowlist appears.

## GitHub Copilot CLI (`copilot-cli`)

- Source URL: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- Last verified: `2026-06-04`
- `audit_kind`: `name-allowlist`
- Frontmatter: `tools` as `yaml-list`

The audit compares configured tool names with this runtime block and reports unknown, legacy, or cross-runtime names. Scope values distinguish shared Copilot/VS Code entries from product-specific entries.

| Tool name | Category | Scope | Aliases |
|---|---|---|---|
| `vscode` | execute | `both` | — |
| `execute` | execute | `both` | `shell`, `Bash`, `powershell` |
| `read` | read | `both` | `Read`, `NotebookRead` |
| `edit` | write | `both` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` |
| `search` | search | `both` | `Grep`, `Glob` |
| `agent` | delegation | `both` | `custom-agent`, `Task` |
| `web` | web | `both` | `WebSearch`, `WebFetch` |
| `todo` | todo | `both` | `TodoWrite` |

| Profile | Tool list |
|---|---|
| `standard` | `vscode`, `execute`, `read`, `agent`, `edit`, `search`, `todo` |
| `read-only` | `read`, `search` |
| `runner` | `execute`, `read`, `search`, `todo` |
| `research` | `read`, `search`, `web`, `todo` |
| `inherit` | `inherit` (omit key) |

Notes: The Standard Tool Profile includes the `vscode` alias because it is the established cross-surface default — VS Code Copilot activates IDE integration with it, and Copilot CLI silently ignores it when not running under VS Code. Other `scope: cli-only` or `scope: vscode-only` tools (if any are added in future catalog updates) require explicit opt-in for shared `.github/agents/*.agent.md` files per hard rule #39.

## VS Code Copilot (`vscode-copilot`)

- Source URL: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- Last verified: `2026-06-04`
- `audit_kind`: `name-allowlist`
- Frontmatter: `tools` as `yaml-list`

The audit compares configured tool names with this runtime block and reports unknown, legacy, or cross-runtime names. Scope values distinguish shared Copilot/VS Code entries from product-specific entries.

| Tool name | Category | Scope | Aliases |
|---|---|---|---|
| `vscode` | execute | `vscode-only` | — |
| `agent` | delegation | `both` | — |
| `edit` | write | `both` | — |
| `execute` | execute | `both` | — |
| `read` | read | `both` | — |
| `search` | search | `both` | — |
| `todo` | todo | `both` | — |
| `web` | web | `both` | — |
| `search/codebase` | search | `vscode-only` | — |
| `search/usages` | search | `vscode-only` | — |
| `web/fetch` | web | `vscode-only` | — |
| `read/terminalLastCommand` | read | `vscode-only` | — |

| Profile | Tool list |
|---|---|
| `standard` | `agent`, `read`, `edit`, `search`, `todo` |
| `read-only` | `read`, `search` |
| `planner-ide` | `search/codebase`, `search/usages`, `web/fetch` |
| `implementer-ide` | `edit`, `read/terminalLastCommand` |
| `inherit` | `inherit` (omit key) |

Notes: Shared `.github/agents/*.agent.md` file format with Copilot CLI. Tools with `scope: vscode-only` are silently ignored by Copilot CLI and require explicit opt-in for shared files.

## Claude Code (`claude-code`)

- Source URL: https://docs.claude.com/en/docs/claude-code/sub-agents
- Last verified: `2026-06-04`
- `audit_kind`: `name-allowlist`
- Frontmatter: `tools` as `comma-string`

The audit compares configured tool names with this runtime block and reports unknown, legacy, or cross-runtime names. Scope values distinguish shared Copilot/VS Code entries from product-specific entries.

| Tool name | Category | Scope | Aliases |
|---|---|---|---|
| `Read` | read | `both` | — |
| `Write` | write | `both` | — |
| `Edit` | write | `both` | — |
| `Bash` | execute | `both` | — |
| `Grep` | search | `both` | — |
| `Glob` | search | `both` | — |
| `Agent` | delegation | `both` | `Task` |
| `WebFetch` | web | `both` | — |
| `WebSearch` | web | `both` | — |
| `TodoWrite` | todo | `both` | — |
| `AskUserQuestion` | interaction | `both` | — |
| `Task` | delegation | `both` | `Agent` |

| Profile | Tool list |
|---|---|
| `standard` | `Read`, `Write`, `Edit`, `Bash`, `Grep`, `Glob`, `TodoWrite` |
| `read-only` | `Read`, `Grep`, `Glob` |
| `researcher` | `Read`, `Grep`, `Glob`, `WebFetch`, `WebSearch` |
| `main-thread-coordinator` | `Agent`, `Read`, `Bash` |

Notes: Tool names are case-sensitive. `tools:` is a comma-separated string in frontmatter (NOT a YAML list). `disallowedTools:` is a separate frontmatter key, not a tool. Current Claude Code docs say `Agent`, `Task`, and `AskUserQuestion` are not available inside spawned subagents even when listed; use them only where the runtime supports main-thread agent execution, otherwise subagents return `question_request`.

## OpenCode (`opencode`)

- Source URL: https://opencode.ai/docs/agents/
- Last verified: `2026-06-04`
- `audit_kind`: `permission-policy`
- Frontmatter: `permission` as `nested-permission-map`

The audit parses the nested permission map, checks broad wildcard policy, and rejects deprecated `tools:` usage rather than comparing a flat tool list.

| Permission key | Values | Scope | Aliases |
|---|---|---|---|
| `read` | `allow`, `ask`, `deny`, `<file-pattern-map>` | policy | — |
| `edit` | `allow`, `ask`, `deny`, `<file-pattern-map>` | policy | — |
| `glob` | `allow`, `ask`, `deny`, `<glob-pattern-map>` | policy | — |
| `grep` | `allow`, `ask`, `deny`, `<grep-pattern-map>` | policy | — |
| `list` | `allow`, `ask`, `deny`, `<path-pattern-map>` | policy | — |
| `bash` | `allow`, `ask`, `deny`, `<command-pattern-map>` | policy | — |
| `task` | `allow`, `ask`, `deny`, `<roster-agent-map>` | policy | — |
| `external_directory` | `allow`, `ask`, `deny`, `<path-pattern-map>` | policy | — |
| `todowrite` | `allow`, `ask`, `deny` | policy | — |
| `webfetch` | `allow`, `ask`, `deny` | policy | — |
| `websearch` | `allow`, `ask`, `deny` | policy | — |
| `codesearch` | `allow`, `ask`, `deny` | policy | — |
| `lsp` | `allow`, `ask`, `deny`, `<operation-pattern-map>` | policy | — |
| `skill` | `allow`, `ask`, `deny`, `<skill-name-map>` | policy | — |
| `question` | `allow`, `ask`, `deny` | policy | — |
| `doom_loop` | `allow`, `ask`, `deny` | policy | — |

Notes: OpenCode uses a nested permission map, NOT a tools allowlist. The old `tools:` key is deprecated upstream. Audit checks: wildcard default must be `deny` or `ask` for `task` and `skill` keys; explicit `allow` entries must be named (no `*: allow`).

## OpenAI Codex (CLI + App) (`codex`)

- Source URL: https://developers.openai.com/codex/subagents
- Last verified: `2026-06-04`
- `audit_kind`: `n/a-unless-explicit`
- Frontmatter: `tool_allowlist` as `toml-array`

The audit skips this runtime unless a custom `tool_allowlist` appears, because the default behavior is inherited session tools.

| Tool name | Category | Scope | Aliases |
|---|---|---|---|
| — | — | — | — |

Notes: Codex subagents inherit the parent session toolbelt by default. Per-agent `tool_allowlist` is optional. Catalog audit is n/a unless `tool_allowlist` is explicitly set in a subagent TOML; in that case, the allowlist names must follow the parent session conventions. Validate `sandbox_mode` (read-only | workspace-write | danger-full-access) and MCP entries instead.

## Gemini CLI (`gemini-cli`)

- Source URL: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md
- Last verified: `2026-06-04`
- `audit_kind`: `name-allowlist`
- Frontmatter: `tools` as `yaml-list`

The audit compares configured tool names with this runtime block and reports unknown, legacy, or cross-runtime names. Scope values distinguish shared Copilot/VS Code entries from product-specific entries.

| Tool name | Category | Scope | Aliases |
|---|---|---|---|
| `read_file` | read | `both` | — |
| `grep_search` | search | `both` | — |
| `run_shell_command` | execute | `both` | — |
| `ask_user` | interaction | `both` | — |

| Profile | Tool list |
|---|---|
| `standard` | `read_file`, `grep_search`, `run_shell_command` |
| `read-only` | `read_file`, `grep_search` |
| `interactive` | `read_file`, `grep_search`, `ask_user` |
| `inherit` | `inherit` (omit key) |

Unverified candidates for a future parser-backed refresh: `glob`, `list_directory`, `read_many_files`, `write_file`, `edit`, `web_fetch`, `google_web_search`, `save_memory`.

Verified wildcard forms: `*`, `mcp_*`, `mcp_<server>_*`.

Notes: Gemini local subagents cannot recursively delegate; tools that spawn sub-tasks (for example, `task` / `agent`) are not part of the Gemini local-subagent tool surface. The upstream subagents docs verify `read_file`, `grep_search`, `run_shell_command`, `ask_user`, and wildcard forms; other common Gemini tool names remain candidates until a parser-backed refresh lands.

## Audit kinds reference

| Audit kind | Runtimes | What the audit skill validates |
|---|---|---|
| `name-allowlist` | Copilot CLI, VS Code Copilot, Claude Code, Gemini CLI | Parses agent frontmatter, extracts configured tool names, and emits findings for unknown names, legacy names, cross-runtime leaks, and missing catalog stamps. |
| `permission-policy` | OpenCode | Parses `permission:`, verifies no deprecated `tools:` key is present, checks `task` and `skill` wildcard defaults, and verifies named allows refer to real roster agents or skills. |
| `n/a-unless-explicit` | OpenAI Codex | Skips default inherited tools. If `tool_allowlist` is explicitly set, validates names using Codex parent-session semantics and separately checks sandbox/MCP shape. |

## Anti-patterns

- Copying Copilot tool names verbatim into a Claude file. Names like `vscode` and `execute` are not Claude Code tool names and can be silently ignored or misread.
- Using `tools:` in OpenCode agents. `tools:` is deprecated upstream; new output must use a `permission:` block and gate `task` / `skill` wildcards safely.
- Treating Codex `tool_allowlist` as required. Codex inherits session tools by default, so explicit allowlists should be rare and reviewed.
- Emitting `scope: vscode-only` tools in shared `.github/agents/*.agent.md` files without explicit opt-in. Default emitters include only `scope: both` tools.

## Source citations

- `copilot-cli`: https://docs.github.com/en/copilot/reference/custom-agents-configuration — last verified `2026-06-04`.
- `vscode-copilot`: https://code.visualstudio.com/docs/copilot/customization/custom-agents — last verified `2026-06-04`.
- `claude-code`: https://docs.claude.com/en/docs/claude-code/sub-agents — last verified `2026-06-04`.
- `opencode`: https://opencode.ai/docs/agents/ — last verified `2026-06-04`.
- `codex`: https://developers.openai.com/codex/subagents — last verified `2026-06-04`.
- `gemini-cli`: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md — last verified `2026-06-04`.
