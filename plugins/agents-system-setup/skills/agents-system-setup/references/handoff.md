# Plan Handoff Contract

Use this contract whenever upstream planning output is handed to the generated orchestrator or subagents. It hardens handoff from planning surfaces into runtime-correct agent artifacts.

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
| Copilot CLI | Markdown body in `.github/agents/<name>.agent.md` | YAML frontmatter must use `name`, `description`, optional `tools`, and optional `mcp-servers`; handoff fields stay in body sections. |
| Claude Code | Markdown body in `.claude/agents/<name>.md` | YAML frontmatter must use Claude fields such as `name`, `description`, and comma-string `tools`; do not copy Copilot tool lists. |
| OpenCode | Markdown body in `.opencode/agents/<name>.md` | Frontmatter has no `name`; filename is the agent name. Use `description`, `mode`, and `permission`; MCP stays in `opencode.json`. |
| OpenAI Codex (CLI + App) | `developer_instructions` in `.codex/agents/<name>.toml`; orchestrator summary in `AGENTS.md` | TOML must include `name`, `description`, and `developer_instructions`. Specialized subagents are not Markdown headings in `AGENTS.md`. CLI-only instructions such as `/agent` are usage notes, not required App behavior. |
| Gemini CLI | Markdown body in `.gemini/agents/<name>.md`; root-session summary in `GEMINI.md` pointing to `AGENTS.md` | YAML frontmatter must use `name`, `description`, optional `kind: local`, and snake_case `mcp_servers`. Handoff text tells subagents to return cross-agent work to the root session because Gemini subagents cannot recursively call subagents. |

Skills are portable `SKILL.md` files; if a skill consumes handoff data, describe the HandoffIR fields in the skill body rather than inventing runtime-specific frontmatter.

## Delegation packet (canonical schema)

The orchestrator passes subagents a **Task Assignment**. Renderers fill the same fields in the same order. **This section is the single source of truth** — `references/context-optimization.md` and every orchestrator template must reference it instead of redefining it. The packet has two layers: a Required Minimum (always sent) and Expansion Blocks (sent when applicable).

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

Assumptions:
  - <assumption the orchestrator made; subagent may challenge>

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
```

### Recommended Packet Form

| Task tag | Recommended form | Required expansion blocks (in addition to required minimum) |
|---|---|---|
| `read-only-research` | short-form | none |
| `content-quality-review` | short-form | Reporting Protocol |
| `code-edit` (≤2 files, no gates) | short-form | none |
| `code-edit` (>2 files or touching shared boundary) | full-form | Goal & Definition of Done · Scope · File Inventory · Verification Protocol · Reporting Protocol |
| `security-write` | full-form | Goal & Definition of Done · Scope · File Inventory · Known Risks · Verification Protocol · Reporting Protocol · Clarification Protocol |
| `mcp-write` | full-form | Goal & Definition of Done · Scope · File Inventory · Known Risks · Reporting Protocol · Clarification Protocol |
| `replication` | full-form | Goal & Definition of Done · Scope · File Inventory · Verification Protocol · Reporting Protocol · Coordination |
| `release` | full-form | Goal & Definition of Done · Verification Protocol · Reporting Protocol · Known Risks |
| `docs-only` | short-form | Reporting Protocol when docs CI exists |
| `bug-fix` | full-form | Goal & Definition of Done · Reproduction · Verification Protocol · Reporting Protocol |

Use full-form whenever the task touches MCP, secrets, CI/release, dependency manifests, generated scripts, ADRs, or fan-out waves — even if the table above suggests short-form.

Do not include unrelated roster rows, marketplace research, or full platform schema details unless the task is generating or validating agent files. When the orchestrator already loaded `AGENTS.md` for the current turn, set `Context freshness: recent` so the subagent skips redundant re-reads (see [context-optimization](./context-optimization.md#context-freshness-rule)).

### Acceptance Checklist

Subagents run this before doing work and return one consolidated `question_request` if any required field is missing.

1. All twelve required-minimum fields are present and non-empty: Task, Source plan, Owned paths, Read-only paths, Relevant gates, Constraints, Dependencies / wave, Required approvals, Runtime format target, Expected output, Context freshness, and Lossiness.
2. `File Inventory.to_modify` (when used) intersects only `Owned paths`.
3. `File Inventory.to_read_only` (when used) does not include any path the agent owns exclusively.
4. `Required approvals` lists every approval the task could trigger, or `none`.
5. `Verification Protocol` is provided when the task is full-form; otherwise fall back to `AGENTS.md` › Quality Gates.
6. `Reporting Protocol` matches the orchestrator's expected evidence shape.
7. `Constraints` and `Known Risks` mention every gate the agent will touch.
8. `Coordination` lists wave siblings when `Dependencies / wave` is greater than 1.

If any check fails, return: `question_request: <single consolidated question>` and stop. Do not loop.

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
Content quality: ok | warn | fail | n/a; signals=<list|none>
Risks / escalations: <list or "none">
Handoff status: accepted | completed | blocked | returned-to-orchestrator
Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>
```

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

## Anti-patterns

- Copying `agent: Plan` into generated agent frontmatter.
- Treating Spec-Kit `/plan` metadata as a subagent schema.
- Emitting a Copilot `tools:` list into Claude Code or OpenCode files.
- Writing OpenCode MCP config into agent frontmatter instead of `opencode.json`.
- Rendering Codex specialized subagents as Markdown headings in `AGENTS.md`.
- Treating Codex CLI commands as requirements for Codex App compatibility.
- Copying Gemini extension `mcpServers` examples into local `.gemini/agents/*.md` instead of normalizing to `mcp_servers`.
- Treating content-quality review as a replacement for tests, security review, architecture review, or provider schema validation.
