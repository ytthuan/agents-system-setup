# Prompt Guidelines for Main-to-Subagent Handoff

Audience: orchestrators, generators, replication logic, and prompt-quality
reviewers. Runtime subagents should not load this reference by default; in other
words, do not load this reference by default from generated runtime subagents.
They use the compact **Plan Handoff Contract** and **Assignment Intake** embedded
in their generated agent files.

Use this guide to compose high-signal Task Assignments from a main agent to a
subagent. The goal is not a longer prompt. The goal is a smaller, clearer
subtask slice that includes the decisions, boundaries, and expected output a
specialist needs to act safely.

## Source-backed principles

| Principle | Applied rule | Source family |
|---|---|---|
| Clear trigger and role | Start each agent description with concrete "Use when..." triggers and keep one durable concern per subagent. | GitHub Copilot custom-agent docs; Claude Code subagent docs; OpenCode agent docs |
| Isolated context | Send only the subtask slice; do not paste full project memory or full plans into every worker. | Copilot CLI subagents; Claude Code subagents; Codex subagent concepts; Gemini CLI subagents |
| Least privilege | Describe allowed capabilities and approval-gated actions in runtime-neutral terms, then render native tool or permission syntax per platform. | Copilot custom-agent tool aliases; Claude tools; OpenCode permissions; Codex sandbox; Gemini tools |
| Stable output | Require a compact reporting block so the orchestrator can integrate results without re-deriving scope, evidence, or risks. | Copilot task subagent summaries; Claude subagent result summaries; Codex consolidated results |
| Human escalation | Missing user input becomes one `question_request`; gated writes stop before risk instead of silently assuming approval. | Provider-native question tools and plugin human-input policy |
| App-compatible artifacts | Codex project artifacts must not require CLI-only slash commands to be useful in Codex App surfaces that load repo artifacts. | OpenAI Codex subagent docs |

## Orchestrator Assignment Format

For normal, risky, multi-file, fan-out, MCP, release, replication, security,
architecture, or generated-agent-system work, orchestrators compose this shape
before invoking a subagent. Safe tiny tasks may use short-form, but should still
include the Required Minimum from [handoff](./handoff.md#required-minimum) when
practical.

```text
Task: <one sentence>
Source plan: <user request | Spec-Kit /plan | VS Code plan prompt | other>
Triage: <separate | merged | skipped | n/a, question_request count>
Content quality: <ok | warn | fail | n/a, curator=<mode>, signals=<list|none>>
Owned paths: <paths from Directory Architecture>
Read-only paths: <paths for context only>
Relevant gates: <quality/security gates>
Constraints: <security/architecture/runtime constraints>
Dependencies / wave: <wave and waits_for>
Required approvals: <mcp | secrets | ci | user-scope | none>
Runtime format target: <none | platform path + schema>
Expected output: <files changed, evidence, risks>
Context freshness: <AGENTS.md@sha | recent | reload>
Lossiness: <fields dropped or mapped, or "none">

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
  - <observable outcome>

Verification Protocol:
  build: <command or "n/a">
  test: <command or "n/a">
  lint: <command or "n/a">
  security: <command/evidence or "n/a">
  manual: <smoke step or "n/a">

Reporting Protocol:
  required_evidence:
    - <diff summary | test output | risk update>
  format: <structured block | markdown bullets | plain prose>

Stop / Escalation Conditions:
  - <condition> -> <return-to-orchestrator | question_request | stop-before-write>
```

## Assignment-quality status

Every subagent result should include:

```text
Task assignment quality: ok | warn | fail; form=<short|full>; missing=<fields|none>; questions=<count>
```

Use these statuses:

| Status | Meaning |
|---|---|
| `ok` | Required fields needed for this task were present; expansion blocks matched the task risk. |
| `warn` | Safe short-form work could continue, but a non-blocking field was missing or inferred. |
| `fail` | A missing or conflicting field blocks safe work, hides an approval, or crosses ownership/runtime boundaries. |

`warn` is acceptable for safe, reversible, tiny tasks. `fail` is required before
MCP, secrets, CI/release, dependency, generated-script, artifact-tracking,
runtime-schema, or unclear-ownership writes.

## Context Packet rule

The orchestrator extracts the per-subtask slice. It must not paste:

- the full `AGENTS.md` managed block;
- the full `plan.md`;
- unrelated logs or search results;
- full platform schemas when only one runtime row is needed;
- full marketplace research when a selected candidate summary is enough.

Use `Context freshness: recent` or `AGENTS.md@<sha>` when the orchestrator has
already loaded project memory in the current turn. Use `reload` for replication,
update mode, or stale context.

## Allowed capabilities and skills

Use provider-neutral wording in the Task Assignment:

- **Allowed capabilities** means the runtime-correct tool, permission, sandbox,
  or profile surface.
- **Approval-gated actions** means actions that still require user/security
  approval before write.
- **Skills referenced** means existing, installed, or generated skills only.
  Never invent skill names or invocation syntax to make an assignment look
  complete.

Runtime mapping happens in [platforms](./platforms.md) and
[agent-format](./agent-format.md). The prompt contract never asks a subagent to
mutate its own frontmatter or TOML.

## Provider notes

| Runtime | Handoff note |
|---|---|
| Copilot CLI | Use public tool aliases in agent files. `ask_user` is session-level; custom agents return `question_request`. |
| Claude Code | Use Claude tool names and optional `skills`; restrictive ask-capable agents may include `AskUserQuestion`. |
| OpenCode | Use `permission`, especially `question` and `task`; do not describe new behavior with deprecated `tools` maps. |
| OpenAI Codex CLI + App | Keep all assignment guidance inside `developer_instructions`; no TOML fields for tools, question, memory, context packet, or expected output. |
| Gemini CLI | Local subagents cannot recursively call subagents; return cross-agent work to the root/orchestrator session. |

## Anti-patterns

- Delegating a bare prompt for normal or risky work.
- Sending the whole plan to every worker.
- Hiding approval-gated actions inside generic "use tools as needed" wording.
- Listing skills or MCP servers that were not installed, generated, or approved.
- Treating assignment quality as a substitute for tests, security review,
  content quality, architecture review, or provider schema validation.
