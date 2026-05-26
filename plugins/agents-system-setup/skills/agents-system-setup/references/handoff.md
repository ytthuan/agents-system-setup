# Plan Handoff Contract

Use this contract whenever upstream planning output is handed to the host orchestrator (the CLI session) or subagents. It hardens handoff from planning surfaces into runtime-correct agent artifacts.

This contract is also the **Task Assignment / Prompt Contract** for
orchestrator-to-subagent delegation. The machine-readable schema lives here; the
prompt-authoring guide lives in [prompt guidelines](./prompt-guidelines.md).

## Source prompt

VS Code Insiders ships a `plan.prompt.md` prompt with this shape:

```yaml
---
name: plan
description: Research and plan with the Plan agent
agent: Plan
argument-hint: Describe what you want to plan or research
---
Plan my task.
```

Treat this as an upstream planning surface only. The `agent: Plan` field routes the prompt to a planner; it is not valid Copilot CLI, Claude Code, OpenCode, OpenAI Codex, or Gemini CLI subagent frontmatter. Spec-Kit `/plan` and user-written plans follow the same rule: parse the planning output into HandoffIR, then render the selected runtime's native format.

`requirements-triage` output is also upstream planning input. Treat its intake
brief as a plan seed: useful for scope, risks, questions, and routing, but not a
final approval or runtime schema.

## HandoffIR

Normalize every plan handoff into these fields before delegation or file generation:

```yaml
task: "<one sentence>"
source_plan: "vs-code-plan-prompt | spec-kit-plan | user-plan | other"
triage_source: "requirements-triage | planner-merged | skipped | n/a"
triage_status: "separate | merged | skipped | n/a"
content_quality_status: "ok | warn | fail | n/a"
content_quality_curator: "separate | merged | skipped | n/a"
content_quality_signals: ["generic-description | empty-rationale | padding-repetition | slop-completeness | invented-attribution | context-bloat | vague-ownership | unsupported-assertion | silent-gate-gap | prompt-hygiene-risk | none"]
assignment_quality_status: "ok | warn | fail | n/a"
assignment_quality_form: "short | full | n/a"
assignment_quality_missing: ["<field>", "...", "none"]
assignment_quality_questions: <integer>
selected_platforms: ["copilot-cli", "claude-code", "opencode", "codex-cli", "gemini-cli"]
owning_agent: "<kebab-case agent name>"
owned_paths: ["<glob>", "..."]
read_only_paths: ["<glob>", "..."]
relevant_gates: ["<quality/security gate>", "..."]
dependencies:
  wave: <integer>
  waits_for: ["<agent-or-task>", "..."]
required_approvals: ["mcp-config | secrets | ci-release | user-scope | none"]
runtime_format_target: "<platform path + schema>"
expected_output: ["<file or evidence>", "..."]
evidence_required: ["diff summary", "tests", "security finding", "adr", "..."]
lossiness: ["<field dropped or mapped>", "..."]
surface_lossiness: ["<CLI-only instruction not available in app/web UI>", "..."]
```

## Requirements triage handoff

When `requirements-triage` runs, it returns this compact intake brief before the
orchestrator writes the plan:

```text
Intent summary: <one sentence>
Task type: init | update | improve | replicate | release | docs | research | unknown
Scope:
  in: <items>
  out: <items>
Ambiguities:
  - <missing detail or "none">
Question requests:
  - <question_request id or "none">
Risk classification:
  security: low | medium | high
  mcp_or_external_tools: yes | no
  release_or_ci: yes | no
Recommended routing:
  wave_0: <agents to consult before plan>
  wave_1: <parallel-safe implementation agents>
Plan seed:
  acceptance_criteria: <bullets>
  suggested_quality_gates: <bullets>
Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>
```

The orchestrator validates this brief, resolves any `question_request` through
the Human Input / Question Protocol, then converts accepted fields into the
normal HandoffIR. Triage cannot approve MCP writes, artifact tracking, release
actions, learning overwrites, or security-sensitive changes.

## Per-runtime handoff surfaces

| Runtime | Where the handoff lives | Format rule |
|---|---|---|
| Copilot CLI | **Orchestrator role: `AGENTS.md` › Orchestration Operating Model** (host CLI session). Specialized subagents: Markdown body in `.github/agents/<name>.agent.md` | Subagent YAML frontmatter must use `name`, `description`, optional `tools`, and optional `mcp-servers`; handoff fields stay in body sections. No `orchestrator.agent.md` file is emitted. |
| Claude Code | **Orchestrator role: `AGENTS.md` › Orchestration Operating Model** (host Claude Code session via `CLAUDE.md` pointer). Specialized subagents: Markdown body in `.claude/agents/<name>.md` | Subagent YAML frontmatter must use Claude fields such as `name`, `description`, and comma-string `tools`; do not copy Copilot tool lists. No `.claude/agents/orchestrator.md` file is emitted. |
| OpenCode | **Orchestrator role: `AGENTS.md` › Orchestration Operating Model** (host OpenCode root session, native `AGENTS.md` reader). Specialized subagents: Markdown body in `.opencode/agents/<name>.md` | Subagent frontmatter has no `name`; filename is the agent name. Use `description`, `mode: subagent`, and `permission`; MCP and the root-session `permission.task` subagent-gating stay in `opencode.json`. No `.opencode/agents/orchestrator.md` file is emitted. |
| OpenAI Codex (CLI + App) | **Orchestrator role: `AGENTS.md` › Orchestration Operating Model** (host Codex session, native `AGENTS.md` reader). Specialized subagents: `developer_instructions` in `.codex/agents/<name>.toml` | TOML must include `name`, `description`, and `developer_instructions`. Specialized subagents are not Markdown headings in `AGENTS.md`. CLI-only instructions such as `/agent` are usage notes, not required App behavior. No `.codex/agents/orchestrator.toml` is emitted (Codex has always followed this pattern). |
| Gemini CLI | **Orchestrator role: `AGENTS.md` › Orchestration Operating Model** (host Gemini session via `GEMINI.md` pointer). Specialized subagents: Markdown body in `.gemini/agents/<name>.md` | Subagent YAML frontmatter must use `name`, `description`, optional `kind: local`, and snake_case `mcp_servers`. Handoff text tells subagents to return cross-agent work to the host root session because Gemini subagents cannot recursively call subagents. No `.gemini/agents/orchestrator.md` file is emitted. |

Skills are portable `SKILL.md` files; if a skill consumes handoff data, describe the HandoffIR fields in the skill body rather than inventing runtime-specific frontmatter.

## Runtime-native delegation syntax

Use the same HandoffIR for every provider, then express delegation in the
runtime's native coordination surface. Do not copy these call-surface notes into
another provider's frontmatter or TOML.

| Runtime | Native delegation surface | Handoff rule |
|---|---|---|
| Copilot CLI / VS Code | Task/custom-agent call via the `agent` tool; optional `/fleet` prompt for independent batches | Use Task/agent fan-out when results need orchestrator synthesis. Treat `/fleet` as optional CLI UX, not required artifact behavior. |
| Claude Code | `Agent` tool for normal subagent work; experimental Agent Teams only when enabled | Fan out multiple `Agent` calls for independent wave members. Return `question_request` from background/headless workers instead of relying on `AskUserQuestion`. |
| OpenCode | `task` permission plus `@<agent-name>` routing from a primary agent | Primary agents use `permission.task` with wildcard `deny`/`ask` and named roster allows, or an explicit skipped-roster marker. |
| OpenAI Codex (CLI + App) | Root `AGENTS.md` asks Codex to spawn child agents; specialists live in `.codex/agents/*.toml` | Keep shared artifacts free of required CLI-only slash commands. Use `.codex/config.toml` `[agents] max_depth = 1` unless the user approves deeper recursion. |
| Gemini CLI | Root Gemini session delegates to local subagents by description or `@<agent-name>` | Keep all fan-out in the root session because Gemini subagents cannot recursively call other subagents. |

## Delegation packet (canonical schema)

The host orchestrator passes subagents a **Task Assignment**. Renderers fill the same fields in the same order. **This section is the single source of truth** — `references/context-optimization.md` and every host-orchestrator section in `AGENTS.md` must reference it instead of redefining it. The packet has two layers: a Required Minimum (always sent) and Expansion Blocks (sent when applicable).

### Required minimum

```text
Task: <one sentence>
Source plan: <user request | VS Code plan prompt | Spec-Kit /plan | other>
Owned paths: <paths from Directory Architecture>
Read-only paths: <paths for context only>
Relevant gates: <quality/security gates>
Constraints: <security/architecture constraints>
Dependencies / wave: <wave and waits_for>
Required approvals: <mcp | secrets | ci | user-scope | none>
Runtime format target: <none | platform path + schema>
Expected output: <files changed, evidence, risks>
Context freshness: <AGENTS.md@<sha or "recent"> | reload>
Lossiness: <fields dropped or mapped, or "none">
```

These twelve fields are mandatory in every assignment. Add
`Triage: <separate | merged | skipped | n/a, question_request count>` immediately
after `Source plan` when the setup includes `requirements-triage`; it is strongly
recommended but not counted in the required minimum so older generated systems
remain compatible. The twelve required fields preserve backward compatibility
with the legacy Delegation Packet name.

Add `Content quality: <ok | warn | fail | n/a, curator=<separate|merged|skipped>, signals=<list|none>>`
after `Triage` when the task creates or changes generated agent, skill, memory,
recommendation, or output-contract prose. It is strongly recommended but not
part of the required minimum for backward compatibility.

Add `Task assignment quality: <ok | warn | fail; form=<short|full>; missing=<fields|none>; questions=<count>>`
after `Content quality` when the host orchestrator delegates to a subagent.
It is recommended by default and required in generated reporting templates, but
is not part of the twelve required-minimum fields for backward compatibility.

### Expansion blocks

Add only the blocks the task actually needs. Each block has a fixed name so subagents and validators can find it.

```text
Goal & Definition of Done:
  - <observable outcome 1>
  - <observable outcome 2>
  - Done when: <single concrete check>

Scope:
  in_scope:
    - <bullet>
  out_of_scope:
    - <bullet>

Context Packet:
  files:
    - <path or "none">
  facts:
    - <fact from repo/user/runtime docs>
  decisions:
    - <ADR or prior decision>
  references:
    - <reference path or URL>
  do_not_include:
    - <full AGENTS.md | full plan.md | unrelated logs>

File Inventory:
  to_modify:
    - <path>
  to_create:
    - <path>
  to_read_only:
    - <path>
  evidence_sources:
    - <path or url>

Background:
  - <prior decision / ADR id / link>
  - <related issue, PR, commit>
  - <session checkpoint reference>

Reproduction (bug-fix tasks only):
  steps:
    - <step>
  expected: <expected behavior>
  actual: <actual behavior>
  environment: <runtime, version, platform>

Security Analysis (security-team tasks only):
  scope: <diff | repository | report | remediation | program>
  authorization: <owned-code | approved-target | needs-approval>
  asset_or_boundary: <asset/trust boundary>
  candidate_or_finding: <id/title or "n/a">
  validation_status: <confirmed | likely | needs-info | duplicate | not-reproducible | out-of-scope | mitigated | deferred | n/a>
  evidence_required:
    - <source/control/sink | reproduction | counterevidence | severity rationale | proof gaps>

Assumptions:
  - <assumption the orchestrator made; subagent may challenge>

Allowed Capabilities:
  runtime_profile: <read-only | edit-capable | runner | research | inherit>
  approval_gated_actions:
    - <MCP config | secrets | CI/release | dependency write | none>
  disallowed_capabilities:
    - <broad write | recursive subagents | external network | none>

Skills Referenced:
  allowed:
    - <existing skill name or "none">
  invocation_notes: <runtime-correct skill behavior>
  do_not_invent: true

Instructions / Workflow:
  1. <step>
  2. <step>
  3. <step>

Acceptance Criteria:
  - <observable outcome>

Known Risks:
  - <risk> -> <mitigation>

Verification Protocol:
  build: <command or "n/a">
  test: <command or "n/a">
  lint: <command or "n/a">
  security: <command or "n/a">
  manual: <smoke step or "n/a">

Reporting Protocol:
  required_evidence:
    - <diff summary | test output | screenshot | adr addition | risk update>
  format: <markdown bullets | structured block | plain prose>

Coordination:
  wave_siblings:
    - <agent> -> <input/output relationship>
  expected_inputs: <from siblings, if any>
  expected_outputs_for: <siblings consuming this work>

Size & Timebox:
  size: <small | medium | large>
  escalate_if: <e.g., "more than 8 files touched" or "more than 25 tool calls">

Clarification Protocol:
  if_missing_required_field: ask one consolidated question to @orchestrator and wait
  if_assumption_invalid: stop, report, and request revised assignment
  do_not: silently invent missing context

Stop / Escalation Conditions:
  - <condition> -> <return-to-orchestrator | question_request | stop-before-write>

Output Schema:
  required_fields:
    - <Outcome | Files changed | Evidence | Risks | Handoff status>
```

### Recommended Packet Form

| Task tag | Recommended form | Required expansion blocks (in addition to required minimum) |
|---|---|---|
| `read-only-research` | short-form | Context Packet when research sources are preselected |
| `content-quality-review` | short-form | Reporting Protocol |
| `code-edit` (2 or fewer files, no gates) | short-form | Context Packet when prior decisions matter |
| `code-edit` (more than 2 files or touching shared boundary) | full-form | Goal & Definition of Done · Scope · Context Packet · File Inventory · Instructions / Workflow · Verification Protocol · Reporting Protocol |
| `security-write` | full-form | Goal & Definition of Done · Scope · Context Packet · File Inventory · Allowed Capabilities · Known Risks · Verification Protocol · Reporting Protocol · Clarification Protocol · Stop / Escalation Conditions |
| `bug-hunting` | full-form | Goal & Definition of Done · Scope · Security Analysis · Context Packet · File Inventory · Allowed Capabilities · Known Risks · Reporting Protocol · Stop / Escalation Conditions |
| `vulnerability-validation` | full-form | Goal & Definition of Done · Scope · Reproduction · Security Analysis · Context Packet · File Inventory · Verification Protocol · Reporting Protocol · Stop / Escalation Conditions |
| `attack-path-analysis` | full-form | Goal & Definition of Done · Scope · Security Analysis · Context Packet · Evidence · Known Risks · Reporting Protocol |
| `remediation-verification` | full-form | Goal & Definition of Done · Reproduction · Security Analysis · File Inventory · Verification Protocol · Reporting Protocol |
| `disclosure-triage` | full-form | Scope · Security Analysis · Allowed Capabilities · Reporting Protocol · Clarification Protocol · Stop / Escalation Conditions |
| `mcp-write` | full-form | Goal & Definition of Done · Scope · File Inventory · Allowed Capabilities · Known Risks · Reporting Protocol · Clarification Protocol · Stop / Escalation Conditions |
| `replication` | full-form | Goal & Definition of Done · Scope · Context Packet · File Inventory · Verification Protocol · Reporting Protocol · Coordination |
| `release` | full-form | Goal & Definition of Done · Verification Protocol · Reporting Protocol · Known Risks · Stop / Escalation Conditions |
| `docs-only` | short-form | Reporting Protocol when docs CI exists |
| `bug-fix` | full-form | Goal & Definition of Done · Reproduction · Context Packet · Verification Protocol · Reporting Protocol |

Use full-form whenever the task touches MCP, secrets, CI/release, dependency manifests, generated scripts, ADRs, or fan-out waves — even if the table above suggests short-form.

Do not include unrelated roster rows, marketplace research, or full platform schema details unless the task is generating or validating agent files. When the orchestrator already loaded `AGENTS.md` for the current turn, set `Context freshness: recent` so the subagent skips redundant re-reads (see [context-optimization](./context-optimization.md#context-freshness-rule)).

### Acceptance Checklist

Subagents run this before doing work. Safe short-form gaps may continue with
`Task assignment quality: warn`; gated writes, unclear ownership, or runtime
schema ambiguity return one consolidated `question_request` and stop before the
risky action.

1. All twelve required-minimum fields are present and non-empty: Task, Source plan, Owned paths, Read-only paths, Relevant gates, Constraints, Dependencies / wave, Required approvals, Runtime format target, Expected output, Context freshness, and Lossiness.
2. `Context freshness` is explicit (`recent`, an `AGENTS.md` revision, or `reload`) and matches the staleness risk.
3. `File Inventory.to_modify` (when used) intersects only `Owned paths`.
4. `File Inventory.to_read_only` (when used) does not include any path the agent owns exclusively.
5. `Required approvals` lists every approval the task could trigger, or `none`.
6. `Verification Protocol` is provided when the task is full-form; otherwise fall back to `AGENTS.md` › Quality Gates.
7. `Reporting Protocol` matches the orchestrator's expected evidence shape.
8. `Constraints` and `Known Risks` mention every gate the agent will touch.
9. `Coordination` lists wave siblings when `Dependencies / wave` is greater than 1.
10. If the task changes generated agent, skill, memory, recommendation, or output-contract prose, the assignment names the expected Content Quality check or says `n/a`.
11. `Context Packet` is scoped to the subtask and does not paste full project memory, full plans, or unrelated logs.
12. `Allowed Capabilities` and `Skills Referenced` are runtime-neutral and do not ask the agent to invent skills or mutate its own frontmatter/TOML.
13. Security-team tasks include authorization scope, affected asset/boundary, validation status, counterevidence, severity rationale, remediation verification need, and proof-gap reporting.
14. `Output Schema` or `Expected output` is specific enough for the orchestrator to integrate.

If a blocking check fails, return: `question_request: <single consolidated question>` and stop. Do not loop.

### Reporting Template

Subagents emit a stable structure so the orchestrator can integrate without re-deriving:

```text
Outcome: <one sentence>
Files changed: <list with relative paths>
Evidence:
  - <test output>
  - <diff summary>
  - <other evidence per Reporting Protocol>
Gates touched: <list with status>
Task assignment quality: ok | warn | fail; form=<short|full>; missing=<fields|none>; questions=<count>
Content quality: ok | warn | fail | n/a; signals=<list|none>
Security analysis: n/a | scope=<diff|repository|report|remediation|program>; authorization=<owned-code|approved-target|needs-approval>; validation=<confirmed|likely|needs-info|duplicate|not-reproducible|out-of-scope|mitigated|deferred>; severity=<P0|P1|P2|P3|n/a>; proof_gaps=<none|summary>
Risks / escalations: <list or "none">
Question requests: none | <id>
Handoff status: accepted | completed | blocked | returned-to-orchestrator
Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>
```

## Host Orchestrator Lifecycle

These thirteen steps live here so `AGENTS.md` can stay compact while still grounding host-session behavior. The host CLI session runs this lifecycle every time it owns a non-trivial task; subagents do not run it themselves.

1. **Clarify** — If ambiguous and triage cannot resolve it, ask the user one focused question via the provider-native human-input surface (see `AGENTS.md` › Human Input / Question Protocol).
2. **Requirements Triage** — Invoke `@requirements-triage` for ambiguous, risky, cross-runtime, release, MCP, replication, or multi-wave work; otherwise record `triage: skipped` with rationale. Consume the intake brief, risk flags, routing, and `question_request` items before writing the plan.
3. **Plan** — Write `plan.md`. List subtasks, owning agent per subtask (cross-check Directory Architecture), security/architecture impact, acceptance criteria, triage result, and a Plan Handoff packet.
4. **Threat / Architecture check** — If the task touches tools, auth, secrets, dependency manifests, CI/release, data boundaries, APIs, or persistence, delegate to the security and architecture owners before implementation.
5. **Security Team Scope** — For bug hunting, vulnerability validation, attack-path analysis, disclosure triage, or remediation verification, read `AGENTS.md` › Security Team Operating Model and include authorization scope, evidence, counterevidence, severity rationale, and proof gaps in assignments.
6. **Compose Assignment** — Compose a Task Assignment using the Required Minimum 12 fields above. Use full-form for normal/risky work (Context Packet, Allowed Capabilities, Skills Referenced, Workflow, Expected output, Stop/Escalation). Safe tiny tasks may use short-form; security/MCP/CI/release/replication or fan-out waves always use full-form.
7. **Delegate** — Invoke subagents in dependency order using the runtime's native delegation surface (Task/agent tool for Copilot, `Agent` tool for Claude, `task` + `@<agent-name>` for OpenCode, child agent threads for Codex, root-session subagent calls for Gemini). Pass the composed Task Assignment, not the whole project memory.
8. **Integrate** — Collect outputs; reconcile conflicts. If two agents claim the same path, refer to the Directory Architecture.
9. **Resolve Questions** — For each returned `question_request`, ask the user once through the provider-native mechanism when possible. If unavailable, apply safe defaults only for reversible, non-sensitive choices; otherwise record the unresolved request and stop before the gated write. Update plan/todos, then re-delegate.
10. **Verify** — Delegate `@reviewer`, `@tester`, and any required security/architecture owner from Quality Gates. Confirm each subagent passed its Acceptance Checklist or returned a single consolidated `question_request`.
11. **Content Quality Review** — When generated agent-system prose changed, delegate `@agent-quality-curator` or record the merged reviewer check. Require `Content quality: ok|warn|fail|n/a; signals=<list|none>` before final report.
12. **Reflect & Learn** — Collect each subagent's `Learning Check`. Append low-risk new learnings through the memory owner. Sensitive new learnings (tagged `risk` or touching MCP, CI/release, dependencies, secrets, or generated scripts) require host-orchestrator and security-owner approval. Updating, overwriting, or superseding prior learnings requires host-orchestrator approval and evidence. Never store secrets or raw credentials.
13. **Report** — Summarize: changes, verification, security/audit evidence, architecture decisions, pending items, triage status, content-quality status/signals, Task assignment quality (filled fields and question-request count), security-team evidence/proof gaps when applicable, and learning proposals accepted/deferred.

## Wave Execution Playbook

For independent work, the host orchestrator **fans out** all parallel-safe subagents in the current wave in a single host turn using the runtime's native subagent surface. It waits for every result, synthesizes, then starts the next wave. Sequential delegation is allowed only when owned paths overlap, a worker depends on a previous result, or a gate requires review before the next write.

Runtime notes:

- **Copilot CLI** — Task/agent tool fan-out; optional `/fleet` for independent batches (UX, not required).
- **Claude Code** — `Agent` tool calls (multiple in one assistant turn for parallel-safe subagents); experimental Agent Teams when opted in.
- **OpenCode** — `task` permission + `@<agent-name>` routing, gated by `permission.task` in `opencode.json`.
- **OpenAI Codex (CLI + App)** — child agent threads; `.codex/config.toml` `[agents] max_threads` caps concurrency, `max_depth = 1` is the safe default to avoid recursive fan-out.
- **Gemini CLI** — root-session fan-out only; Gemini subagents cannot recursively call other subagents, so the root session owns all wave coordination.

## Memory & Learning Coordination

Subagents return `Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>` as part of their reporting template. The host orchestrator:

1. Collects every subagent's Learning Check before final report.
2. Approves and writes low-risk new learnings through the configured memory owner (see `AGENTS.md` › Memory & Learning System).
3. Routes sensitive proposals (tagged `risk` or touching MCP, CI/release, dependencies, secrets, generated scripts) through host-orchestrator and security-owner approval.
4. Treats updates / overwrites / supersedes of prior learnings as requiring host approval and evidence — never silent merges.
5. Never stores secrets or raw credentials; learnings summarize and point to evidence instead of pasting raw logs.

## Out of Scope (for the host orchestrator)

- Bulk code edits in a subagent's owned path → delegate.
- Long-running implementation work the user expects a specialist to own → delegate.
- Decisions that require product input → bounce to user via `AGENTS.md` › Human Input / Question Protocol.

## Verification

Before declaring done:

1. Confirm every generated `AGENTS.md` contains a non-empty **Plan Handoff Contract** section.
2. Confirm every generated runtime agent includes handoff input/output guidance in the correct surface for that runtime.
3. Parse each target's frontmatter or TOML with the target schema.
4. Confirm any lossy field mapping is in the lossiness report or output contract.
5. Confirm MCP, secrets, CI/release, and user-scope writes still went through their approval gates.
6. For Codex, confirm shared artifacts (`AGENTS.md`, `.codex/agents/*.toml`, `.codex/config.toml`) do not require CLI-only commands to work in the App.
7. For Gemini, confirm `GEMINI.md` points to canonical `AGENTS.md` and `.gemini/agents/*.md` subagents use loader-valid frontmatter.
8. Confirm generated agent-system prose reports `Content quality` status/signals or `n/a`.
9. Confirm the host orchestrator section and generated subagents report `Task assignment quality` and preserve the recommended short-form/full-form semantics.

## Anti-patterns

- Copying `agent: Plan` into generated agent frontmatter.
- Treating Spec-Kit `/plan` metadata as a subagent schema.
- Emitting a Copilot `tools:` list into Claude Code or OpenCode files.
- Writing OpenCode MCP config into agent frontmatter instead of `opencode.json`.
- Rendering Codex specialized subagents as Markdown headings in `AGENTS.md`.
- Treating Codex CLI commands as requirements for Codex App compatibility.
- Copying Gemini extension `mcpServers` examples into local `.gemini/agents/*.md` instead of normalizing to `mcp_servers`.
- Treating content-quality review as a replacement for tests, security review, architecture review, or provider schema validation.
- Treating a bare natural-language instruction as enough context for normal,
  risky, fan-out, MCP, release, replication, security, or generated-agent-system
  work.
