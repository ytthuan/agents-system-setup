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

Treat this as an upstream planning surface only. The `agent: Plan` field routes the prompt to a planner; it is not valid Copilot CLI, Claude Code, OpenCode, or OpenAI Codex subagent frontmatter. Spec-Kit `/plan` and user-written plans follow the same rule: parse the planning output into HandoffIR, then render the selected runtime's native format.

## HandoffIR

Normalize every plan handoff into these fields before delegation or file generation:

```yaml
task: "<one sentence>"
source_plan: "vs-code-plan-prompt | spec-kit-plan | user-plan | other"
selected_platforms: ["copilot-cli", "claude-code", "opencode", "codex-cli"]
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

## Per-runtime handoff surfaces

| Runtime | Where the handoff lives | Format rule |
|---|---|---|
| Copilot CLI | Markdown body in `.github/agents/<name>.agent.md` | YAML frontmatter must use `name`, `description`, optional `tools`, and optional `mcp-servers`; handoff fields stay in body sections. |
| Claude Code | Markdown body in `.claude/agents/<name>.md` | YAML frontmatter must use Claude fields such as `name`, `description`, and comma-string `tools`; do not copy Copilot tool lists. |
| OpenCode | Markdown body in `.opencode/agents/<name>.md` | Frontmatter has no `name`; filename is the agent name. Use `description`, `mode`, and `permission`; MCP stays in `opencode.json`. |
| OpenAI Codex (CLI + App) | `developer_instructions` in `.codex/agents/<name>.toml`; orchestrator summary in `AGENTS.md` | TOML must include `name`, `description`, and `developer_instructions`. Specialized subagents are not Markdown headings in `AGENTS.md`. CLI-only instructions such as `/agent` are usage notes, not required App behavior. |

Skills are portable `SKILL.md` files; if a skill consumes handoff data, describe the HandoffIR fields in the skill body rather than inventing runtime-specific frontmatter.

## Delegation packet

The orchestrator passes subagents a compact packet:

```text
Task: <one sentence>
Source plan: <VS Code plan prompt | Spec-Kit /plan | user plan | other>
Owned paths: <paths from Directory Architecture>
Read-only paths: <paths for context only>
Relevant gates: <quality/security gates>
Dependencies / wave: <wave and waits_for>
Required approvals: <mcp/secrets/ci/user-scope/none>
Runtime format target: <none | platform path + schema>
Expected output: <files changed, evidence, risks>
```

Do not include unrelated roster rows, marketplace research, or full platform schema details unless the task is generating or validating agent files.

## Verification

Before declaring done:

1. Confirm every generated `AGENTS.md` contains a non-empty **Plan Handoff Contract** section.
2. Confirm every generated runtime agent includes handoff input/output guidance in the correct surface for that runtime.
3. Parse each target's frontmatter or TOML with the target schema.
4. Confirm any lossy field mapping is in the lossiness report or output contract.
5. Confirm MCP, secrets, CI/release, and user-scope writes still went through their approval gates.
6. For Codex, confirm shared artifacts (`AGENTS.md`, `.codex/agents/*.toml`, `.codex/config.toml`) do not require CLI-only commands to work in the App.

## Anti-patterns

- Copying `agent: Plan` into generated agent frontmatter.
- Treating Spec-Kit `/plan` metadata as a subagent schema.
- Emitting a Copilot `tools:` list into Claude Code or OpenCode files.
- Writing OpenCode MCP config into agent frontmatter instead of `opencode.json`.
- Rendering Codex specialized subagents as Markdown headings in `AGENTS.md`.
- Treating Codex CLI commands as requirements for Codex App compatibility.
