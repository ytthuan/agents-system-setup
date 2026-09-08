# Adaptive Model and Effort Selection

Use this reference when a user explicitly pins a model/effort, asks for
cost-performance routing, or a delegated task needs a runtime-available
selection. Generated agents omit static model and effort fields by default.

## Default policy: adaptive-balanced

Choose direct versus delegated execution before choosing a worker model.
Delegation has startup, context-transfer, integration, retry, and latency cost;
inheritance is not necessarily cheap.

Apply this precedence:

1. Explicit user and organization provider/model/effort pins.
2. Mandatory quality, safety, independence, and gate requirements.
3. Runtime/provider availability, entitlement, policy, and advertised effort
   controls, within explicit resource and spending limits.
4. Task difficulty and risk.
5. Total expected cost, including retries, cache/startup behavior, and latency.

Explicit pins prevail even when a native per-call override could otherwise
select a stronger or cheaper model. If no allowed model can meet a mandatory
requirement, escalate instead of exceeding budget or silently lowering quality.

## Selection procedure

1. Classify the task: direct host work or delegated, read-only or write,
   bounded or exploratory, routine or high-risk, and whether independent review
   is required.
2. Enumerate only models and effort values advertised by the active runtime.
   Do not rely on a stale newest-model catalog.
3. Select the least expensive option expected to meet the required quality
   with acceptable retry and latency risk. Higher risk or ambiguity may justify
   a stronger model or more effort; routine bounded work usually does not.
4. Prefer per-call selection where supported. If unavailable, inherit the
   configured worker/session choice or propose a separately approved config
   change. Never rewrite a worker definition mid-task for a one-off call.
5. Record the reason when a model is pinned, translated during replication, or
   unavailable.

Do not publish permanent prices, rate limits, or entitlement tables. Link to
current vendor/runtime sources when live commercial details matter.
Unknown prices remain unknown, not free or cheapest. Use verified cost metadata
when available; otherwise preserve an approved choice and disclose uncertainty.
If a hard spending cap cannot be assessed with the available controls/evidence,
stop the affected launch and escalate rather than assume inheritance fits it.

## Runtime resolution facts

| Runtime | Resolution and configuration rule |
|---|---|
| Copilot CLI | Use a per-call/session model only when the active surface advertises it. Agent `model:` remains omitted unless explicitly pinned. |
| Claude Code | Per-call `model` → subagent frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL` → parent. Explicit `inherit` chooses the parent model. |
| OpenCode | Use an advertised configured `provider/model-id`; omitted agent `model:` follows OpenCode/session configuration. |
| Codex CLI + App | Explicit spawn choice → `[agents]` default → parent, except an explicitly selected custom-agent file may pin `model`/`model_reasoning_effort` and override that resolution. Use only currently advertised effort values. |
| Gemini CLI | Local subagent `model:` is optional; omitted values inherit the parent/session choice. Remote agent model selection belongs to the remote service. |

## Replication

- Preserve an explicit source pin as intent, not as a verbatim cross-provider
  identifier.
- Translate only to an available approved target model with equivalent intent.
  A changed explicit pin needs approval and a recorded mapping; availability
  alone is not permission to replace it.
- Preserve unknown imported values for review rather than fabricating a target
  mapping.
- If translation is lossy or impossible, report it in HandoffIR `lossiness`.
- Do not turn an inherited source setting into a static target pin.

## Anti-patterns

- Pinning every worker to one model for consistency.
- Selecting maximum effort for every task.
- Assuming inherited workers use a cheap model.
- Ignoring retry/cache/startup/latency cost.
- Rewriting worker config during a task when no per-call control exists.
- Bypassing user/org pins, provider restrictions, budgets, or mandatory gates.
- Embedding live price, quota, or newest-model catalogs in generated files.

## Sources

- Copilot custom agents:
  <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- Claude Code subagents:
  <https://docs.claude.com/en/docs/claude-code/sub-agents>
- OpenCode agents/providers:
  <https://opencode.ai/docs/agents/> and <https://opencode.ai/docs/providers/>
- Codex subagents and models:
  <https://developers.openai.com/codex/subagents> and
  <https://developers.openai.com/codex/models>
- Gemini CLI subagents:
  <https://geminicli.com/docs/core/subagents/>
