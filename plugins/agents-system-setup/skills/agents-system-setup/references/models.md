# Per-Runtime Model Constraints (optional)

Use this reference whenever a user opts in to setting `model:` overrides during the interview (Q9b) or replicating from a runtime that pinned models. The skill keeps `model:` optional in every emitter; this file is the load-on-demand context that explains *what shape each runtime expects*, *what the default is when omitted*, and *where the live rate/usage limits are documented*.

> Rate limits and quota numbers change frequently and depend on the user's plan tier. **Do not pin RPM, TPM, or daily caps in this repo.** Link to the official sources, then let users open them when they care.

## Decision aid: should the user override `model:`?

Override only when there is a concrete reason. If unsure, leave `model:` blank so the runtime resolves its current default and the agent stays portable across plan changes.

| Situation | Recommended action |
|---|---|
| Reviewer or planner needs deeper reasoning | Override to a higher-tier model on that single agent only |
| Subagent fan-out hits rate limits during waves | Use the runtime default (inherit) for cheap workers; override only the orchestrator/reviewer |
| Replicating from another runtime that pinned a model | Translate to the target runtime's format; never carry the source id verbatim |
| User wants vendor lock-in (e.g., Anthropic-only) | Override per agent and document the choice in `AGENTS.md` |
| Project requires deterministic model id for compliance | Override per agent and pin the exact id; document the deprecation policy |
| User unsure | Skip Q9b; runtime defaults remain in effect |

## Per-runtime model surfaces

### Copilot CLI

- **Field:** `model:` in `.github/agents/<name>.agent.md` frontmatter; `--model <id>` on `copilot` invocation.
- **Default when omitted:** the model selected for the Copilot CLI session inherits.
- **Accepted ids:** internal Copilot model ids (e.g., `claude-sonnet-4.6`, `gpt-5`, `gpt-5-mini`, `claude-opus-4`); the available list depends on the user's Copilot plan and entitlement.
- **Rate limits / availability:** controlled by the user's Copilot plan tier and any organization policy. Sources:
  - <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents>
  - <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
  - <https://docs.github.com/en/copilot/about-github-copilot/plans-for-github-copilot>
- **Override guidance:** keep `model:` blank for portable agent files. Override per agent only when a specific role (e.g., reviewer) consistently benefits from a stronger model.

### Claude Code

- **Field:** `model:` in `.claude/agents/<name>.md` frontmatter; CLI `--model <id>`; `inherit` keeps the session's current model.
- **Default when omitted:** `inherit` (the parent session's selected model).
- **Accepted ids:** alias values `sonnet`, `opus`, `haiku`, plus full Anthropic model ids (e.g., `claude-sonnet-4-5`); the literal `inherit` is also valid.
- **Rate limits / availability:** depend on the user's Claude plan (Free / Pro / Max / Team) and whether the workspace uses Claude API keys directly. Sources:
  - <https://docs.claude.com/en/docs/claude-code/sub-agents>
  - <https://docs.claude.com/en/api/rate-limits>
  - <https://www.anthropic.com/pricing>
- **Override guidance:** prefer aliases (`sonnet`, `opus`, `haiku`) so Claude can roll forward to the latest minor revision without breaking the file. Pin a full id only when compliance demands it.

### OpenCode

- **Field:** `model:` in `.opencode/agents/<name>.md` frontmatter using `provider/model-id` format (e.g., `anthropic/claude-sonnet-4-20250514`).
- **Default when omitted:** the model configured in `opencode.json` for that mode, or the OpenCode session default.
- **Accepted ids:** any `provider/model-id` the configured provider advertises; the provider list is user-controlled.
- **Rate limits / availability:** governed by the configured provider's plan and quota, not by OpenCode itself. Sources:
  - <https://opencode.ai/docs/agents/>
  - <https://opencode.ai/docs/providers/>
  - Provider docs for whichever provider is configured (Anthropic, OpenAI, etc.).
- **Override guidance:** never copy Claude-only aliases like `sonnet` — OpenCode requires `provider/model-id`. Leave blank to defer to `opencode.json`.

### OpenAI Codex (CLI + App)

- **Field:** `model = "<id>"` and optional `model_reasoning_effort = "low|medium|high"` in `.codex/agents/<name>.toml`; `[agents]` defaults live in `.codex/config.toml`.
- **Default when omitted:** inherit from the parent Codex session; the session uses whatever model the user selected in CLI/App.
- **Accepted ids:** OpenAI Codex internal ids (e.g., `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex`); the available set depends on the user's ChatGPT plan and entitlement.
- **Rate limits / availability:** governed by the user's ChatGPT plan (Plus / Pro / Business / Enterprise) plus separate OpenAI API limits for keyed usage. Sources:
  - <https://developers.openai.com/codex/subagents>
  - <https://platform.openai.com/docs/guides/rate-limits>
  - <https://openai.com/chatgpt/pricing/>
- **Override guidance:** when a reviewer needs deep reasoning, set `model_reasoning_effort = "high"` on that agent only; when subagents fan out heavily, leave the model blank so cheap workers inherit a lighter default.

### Gemini CLI

- **Field:** `model:` (and optional `temperature:`) in `.gemini/agents/<name>.md` frontmatter; `kind: local` agents only.
- **Default when omitted:** inherit from the Gemini CLI parent session.
- **Accepted ids:** Gemini model ids documented in the loader schema and Gemini Code Assist docs (e.g., `gemini-3-flash-preview`); availability depends on the user's plan.
- **Rate limits / availability:** governed by the user's Gemini Code Assist plan (Free / Standard / Enterprise) and underlying Google AI quotas. Sources:
  - <https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md>
  - <https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/agents/agentLoader.ts>
  - <https://developers.google.com/gemini-code-assist/resources/quotas-and-limits>
- **Override guidance:** never set `model:` on remote (`kind: remote`) Gemini agents; the remote A2A surface controls its own model. For local subagents, override only when the role needs a different reasoning/speed tradeoff than the root session.

## Anti-patterns

- **Copying ids across runtimes.** `sonnet` is valid for Claude Code but not OpenCode; `gpt-5.4` is valid for Codex but not Copilot CLI. Translate per target.
- **Pinning deprecated ids.** Vendors retire model ids on schedule; prefer aliases (`sonnet`, `opus`, `haiku`, `inherit`) when the runtime supports them.
- **Embedding rate-limit numbers.** RPM, TPM, and daily caps drift with plans and incidents; link to the live source instead.
- **Overriding `model:` on every agent for "consistency".** It blocks the runtime's current default and increases premium-model usage during fan-out.
- **Writing models without `--model`/frontmatter agreement.** When the user supplied a CLI flag default, do not silently override it in agent files unless they asked.
- **Treating remote Gemini A2A agents as configurable models.** Their model lives on the remote service, not in the local file.

## Sources

The links above are the canonical pointers. Re-verify them when adding a new runtime row or before promoting an experimental model to the recommended list.
