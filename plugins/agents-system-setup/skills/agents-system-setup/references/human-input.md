# Provider-Aware Human Input

> Last verified: 2026-05-06. This reference keeps clarification and approval prompts source-backed across supported runtimes.

## Human Input / Question Tool Matrix

| Runtime | Native human-input surface | Emit / allowlist rule | Non-interactive or child-agent fallback |
|---|---|---|---|
| Copilot CLI | Session tool `ask_user`; `--no-ask-user` disables it. | Use from the orchestrator/session. Do **not** add `ask_user` to Copilot custom-agent `tools:` profiles; it is not in the documented custom-agent tool alias table. | Subagents return `question_request`; the orchestrator asks if interactive or records the unresolved request. |
| Claude Code | Tool `AskUserQuestion`. | Include `AskUserQuestion` in restrictive Claude `tools:` allowlists only when that agent is expected to ask the user. Omit the allowlist to inherit. | If not allowed, or when running headless, return `question_request` to the orchestrator. |
| OpenCode | Tool `question`. | Grant with nested permission syntax, for example `permission: { question: allow }` or the YAML block below. Do not write a literal dotted key. | Return `question_request`; the primary agent decides whether to ask, use a safe default, or stop. |
| OpenAI Codex CLI + App | Tool `request_user_input`, available in Plan mode only. | There is no `.codex/agents/*.toml` field for this. Do not emit `request_user_input` or `memory` in agent TOML. | Codex child/default/exec flows return `question_request` to the parent/session. |
| Gemini CLI | Tool `ask_user`. | Valid in Gemini `tools:` allowlists for interactive agents that are expected to ask. | Headless or restricted agents return `question_request`; Gemini subagents still cannot call other subagents. |

OpenCode YAML form:

```yaml
permission:
  question: allow
```

## `question_request` schema

Subagents use this runtime-neutral report when they cannot or should not ask the
human directly:

```yaml
question_request:
  id: <stable-kebab-id>
  asked_by: <agent-name>
  reason: <why the answer is needed>
  question: <one concise question>
  choices: [<optional-choice-1>, <optional-choice-2>]
  default: <safe default or "none">
  urgency: blocking | nonblocking
  if_unanswered: <skip | use_default | stop_before_write>
  context:
    - <fact the orchestrator should show>
```

Rules:

1. Use one question per request. Prefer bounded choices for approvals.
2. Security-sensitive writes (`.mcp.json`, `opencode.json` MCP blocks, secrets-adjacent files, CI/release config, generated scripts) set `if_unanswered: stop_before_write`.
3. When a runtime question tool is disabled, missing from the allowlist, or unavailable in the current mode, keep the `question_request` in the final report instead of guessing.
4. The orchestrator/session maps approved requests to the provider-native tool and records approval evidence in the output contract.

## Generation rules

1. **Orchestrator asks; workers request.** Let the root session or orchestrator call the native question tool. Subagents use `question_request` unless their runtime-specific allowlist explicitly grants a question tool.
2. **Do not synthesize tool names.** Only emit native question tools documented for the target runtime.
3. **Never bypass approval gates.** Human-input tools collect approval; they do not replace the MCP approval gate, artifact-tracking choice, or security evidence requirements.
4. **Headless is safe-by-default.** In non-interactive modes, use safe defaults only for reversible, non-sensitive choices. Otherwise skip or stop before write.
5. **Keep provider syntax exact.** Claude uses `AskUserQuestion`; OpenCode uses nested `permission` with `question`; Codex does not use TOML; Gemini can allow `ask_user`; Copilot custom-agent `tools:` must not include `ask_user`.

## Anti-patterns

- Adding `ask_user` to Copilot custom-agent `tools:` profiles.
- Writing OpenCode `permission.question: allow` as a literal YAML key.
- Emitting `request_user_input` or `memory` fields in Codex agent TOML.
- Letting every subagent ask the user independently and create duplicate prompts.
- Treating `--no-ask-user`, headless, or exec mode as permission to guess security-sensitive answers.
- Using a human-input tool to silently approve MCP or plugin config changes.

## Sources

- Copilot CLI custom-agent docs and config reference: <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents> and <https://docs.github.com/en/copilot/reference/custom-agents-configuration>.
- Claude Code subagents and tools: <https://docs.claude.com/en/docs/claude-code/sub-agents>.
- OpenCode agents and permissions: <https://opencode.ai/docs/agents/>.
- OpenAI Codex subagents and Plan-mode tooling: <https://developers.openai.com/codex/subagents>.
- Gemini CLI subagents, tools, and extensions: <https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md> and <https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md>.
