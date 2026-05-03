# Memory and Learning System

Generated agent systems can include a lightweight learning loop:

```text
Experience -> Capture -> Reflect -> Persist -> Apply
```

The loop is **recommended and non-blocking by default**. Agents should perform a
Learning Check before final response, but `none` is a valid outcome. Memory writes
are approval-safe: subagents propose learnings, while the orchestrator or the
memory owner decides what to persist. The update policy is explicit: **overwrite requires orchestrator approval**.

## Storage profiles

Ask per project before writing memory artifacts.

| Profile | Curated memory | Operational ledger | Use when |
|---|---|---|---|
| `project-tracked` | `docs/agents/learnings.md` | Optional `.agents-system-setup/learnings.jsonl` only after approval | Team wants shared durable learning |
| `project-local` | `.agents-system-setup/memory/learnings.md` or `.agents-system-setup/memory/learnings.jsonl` | `.agents-system-setup/learnings.jsonl` | Personal learning for this checkout |
| `personal-global` | User/global memory path outside the repo | User-local DB/JSONL | Cross-project personal learning |
| `disabled` | none | none | User opts out |

Default guidance: recommend `project-tracked` for teams and `project-local` for
personal setups. Respect the artifact tracking decision from
[local tracking](./local-tracking.md).

## Learning record schema

Use this schema for curated Markdown and JSONL/DB records:

```text
id: <stable-kebab-id>
scope: project | personal | global
category: convention | mistake | preference | tool_insight | workflow | risk
applies_to: <path glob | runtime | agent | command | "all">
summary: <one sentence>
evidence: <file path, command, user correction, PR/issue, or session note>
source_agent: <agent name>
created_or_updated: <date or release/session marker>
status: active | superseded | rejected
supersedes: <id | none>
```

JSONL/DB ledgers may additionally store `confidence`, `hit_count`, and
`last_used`, but generated Markdown should stay compact.

## Learning categories

| Category | Examples | Typical scope |
|---|---|---|
| `convention` | "Use Result<T> instead of exceptions" | project |
| `mistake` | "Do not write operational logs in Markdown agent dirs" | project/global |
| `preference` | "Keep generated agent artifacts project-local" | personal/project |
| `tool_insight` | "Pin markdownlint-cli2@0.13.0 to match CI" | project/global |
| `workflow` | "Run validator before tag push" | project |
| `risk` | "MCP config writes require approval gate" | project |

## Learning Check contract

Before final response, each agent should add one concise Learning Check line to
its report:

```text
Learning Check: none | proposed_new:<id> | proposed_update:<id> | deferred:<reason>
```

When proposing a learning, use this shape:

```text
learning_proposal:
  id: <stable id or "new">
  category: <category>
  scope: <project|personal|global>
  summary: <one sentence>
  evidence: <path/command/user correction/session result>
  applies_to: <paths/runtimes/agents>
  update_policy: append | supersede | overwrite-request
```

`Learning Check: none` is normal when the task produced no durable lesson.

## Write policy

1. Subagents propose learnings; they do not write memory unless the Directory
   Architecture explicitly gives them ownership of the memory path.
2. The orchestrator collects proposals during Integrate / Verify.
3. New low-risk project learnings may be appended by the memory owner.
4. Updating, overwriting, or superseding an old learning requires orchestrator
   approval. The approval must identify the old learning id and the evidence.
5. Superseded learnings are marked `status: superseded`; do not silently delete
   prior memory.
6. If memory storage writes a tracked project file and the run has not already
   approved tracked artifacts, ask before writing.

## Privacy and security rules

- Store no secrets or raw credentials.
- Do not store full env values, access tokens, private keys, personal tokens, or
  redacted-but-reversible values.
- Do not store raw logs when a one-sentence summary and evidence pointer is
  enough.
- Keep operational logs out of Markdown files and out of runtime `agents/`
  directories.
- Treat learnings about security, MCP, CI/release, dependency manifests, or
  generated scripts as security-sensitive evidence.

## Load policy

Agents should load the Learning Index first, then only task-relevant entries:

1. `AGENTS.md` Read First.
2. `AGENTS.md` Memory & Learning System row.
3. Learning Index for matching category/path/runtime.
4. Detailed learning only if the task depends on it.

Do not paste the full learning ledger into every subagent assignment.

## Optional hook/script support

Hooks and scripts may automate capture/reflect/persist, but they are optional and
approval-gated:

- Copilot: project hooks only when the current surface supports them and the user
  approves the exact path/content.
- Claude Code: `.claude/settings.json` hooks only for project/user/session agents;
  plugin-shipped agents must not depend on hooks.
- OpenCode: `.opencode/hooks/` only when selected and approved.
- Codex/Gemini: document agent-native reflection unless a supported hook surface
  is confirmed.

No hook may bypass the MCP approval gate, artifact tracking choice, or
orchestrator approval for overwrites.

## Anti-patterns

- Treating raw command logs as curated memory.
- Writing `.md` operational logs inside `.github/agents/`, `.claude/agents/`,
  `.opencode/agents/`, `.codex/agents/`, or `.gemini/agents/`.
- Letting every subagent append to the same memory file concurrently.
- Updating old learnings without orchestrator approval.
- Storing secrets, raw credentials, or full private logs.
- Loading the entire memory ledger for every task.
